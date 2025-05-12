import json
from sentence_transformers import SentenceTransformer, util
import numpy as np
import time
import gc
import traceback
import psutil
import os
import torch

# Define keywords as per todo.md
LOG_KEYWORDS = {
    'log analysis', 'logstash', 'fluentd', 'rsyslog', 'sumologic',
    'elk', 'kibana', 'kusto', 'splunk', 'graylog', 'papertrail', 'loggly',
    'filebeat', 'root cause', 'observability', 'trace', 'tracing', 'open telemetry',
    'post-mortem', 'anomaly detection', 'prometheus', 'grafana',
    # 'root cause' is repeated, kept one
    'troubleshooting', 'incident investigation',
    'nagios', 'zabbix', 'datadog', 'new relic', 'dynatrace', 'appdynamics'
}

CI_CD_KEYWORDS = {
    'ci/cd', 'continuous integration', 'continuous delivery', 'continuous deployment',
    'jenkins', 'travis', 'circleci', 'github actions', 'gitlab ci',
    'ide', 'unit test', 'test case', 'fullstack', 'database design', 'orm',
    'git commit', 'git push', 'pull request',
    'code review', 'refactoring', 'clean code', 'dynamic programming',
    'teamcity', 'bamboo', 'azure pipelines', 'bitbucket pipelines',
    'build automation', 'artifact repository', 'build artifact',
    'rollback', 'blue-green', 'canary', 'rollout', 'staging',
    'automate build', 'automate test', 'automation script', 'automation tool',
    'automate deployment', 'merge conflict', 'branch strategy', 'trunk-based'
}

# 使用绝对路径确保文件能被正确找到
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(CURRENT_DIR, 'Devops_Stackoverflow_summarization.jsonl')
DEDUPLICATED_FILE = os.path.join(CURRENT_DIR, 'Devops_Stackoverflow_summarization_deduplicated.jsonl')
LOG_RELATED_FILE = os.path.join(CURRENT_DIR, 'Devops_Stackoverflow_summarization_log_related.jsonl')
CICD_RELATED_FILE = os.path.join(CURRENT_DIR, 'Devops_Stackoverflow_summarization_cicd_related.jsonl')

def load_jsonl(file_path):
    """Loads data from a .jsonl file."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def save_jsonl(data, file_path):
    """Saves data to a .jsonl file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"Data saved to {file_path}")

def get_memory_usage():
    """获取当前进程的内存使用情况（MB）"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # 转换为MB

def prepare_texts(data):
    """从数据中提取文本用于嵌入"""
    texts_to_embed = []
    for item in data:
        prompt_text = item.get('prompt', '')
        response_list = item.get('response', [])
        response_text = ''
        if response_list and isinstance(response_list, list):
            for sub_list in response_list:
                if isinstance(sub_list, list):
                    response_text += ' '.join(str(s) for s in sub_list) + ' '
                else:
                    response_text += str(sub_list) + ' '
        texts_to_embed.append(prompt_text + ' ' + response_text.strip())
    return texts_to_embed

def batch_encode_texts(model, texts, batch_size=32, show_progress=True):
    """分批编码文本以减少内存使用"""
    total_texts = len(texts)
    all_embeddings = []
    
    for i in range(0, total_texts, batch_size):
        batch_end = min(i + batch_size, total_texts)
        if show_progress and i % (batch_size * 10) == 0:
            print(f"处理嵌入批次 {i+1}-{batch_end} / {total_texts}")
        
        # 生成当前批次的嵌入向量
        try:
            batch_embeddings = model.encode(texts[i:batch_end], 
                                          convert_to_tensor=True, 
                                          show_progress_bar=(show_progress and i == 0))
            all_embeddings.append(batch_embeddings)
        except Exception as e:
            print(f"编码批次 {i+1}-{batch_end} 时出错: {str(e)}")
            # 尝试减小批次大小并重试
            smaller_batch_size = max(1, batch_size // 2)
            print(f"尝试减小批次大小到 {smaller_batch_size} 并重试...")
            
            for j in range(i, batch_end, smaller_batch_size):
                sub_batch_end = min(j + smaller_batch_size, batch_end)
                try:
                    sub_batch_embeddings = model.encode(texts[j:sub_batch_end], 
                                                      convert_to_tensor=True, 
                                                      show_progress_bar=False)
                    all_embeddings.append(sub_batch_embeddings)
                except Exception as sub_e:
                    print(f"处理子批次 {j+1}-{sub_batch_end} 时出错: {str(sub_e)}")
                    print(f"跳过这些文本并继续...")
        
        # 定期执行垃圾回收
        if i > 0 and i % (batch_size * 50) == 0:
            print(f"执行垃圾回收...")
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            print(f"当前内存使用: {get_memory_usage():.1f} MB")
    
    # 合并所有批次的嵌入向量
    try:
        embeddings = torch.cat(all_embeddings, dim=0)
        return embeddings
    except Exception as e:
        print(f"合并嵌入向量时出错: {str(e)}")
        # 如果无法合并，返回列表形式的嵌入向量
        return all_embeddings

def find_duplicates_with_pytorch(embeddings, similarity_threshold=0.95, batch_size=20, max_vectors_per_batch=100):
    """使用PyTorch批量矩阵操作查找重复项"""
    start_time = time.time()
    
    # 处理嵌入向量可能是列表的情况
    if isinstance(embeddings, list):
        print("警告: 嵌入向量以列表形式提供，将分批处理")
        total_items = sum(batch.shape[0] for batch in embeddings)
    else:
        total_items = embeddings.shape[0]
    
    unique_indices = []
    processed_indices = set()  # 跟踪已处理的项（唯一或重复）
    
    print(f"开始查找重复项，共 {total_items} 个项目...")
    
    # 处理每个嵌入向量
    for i in range(total_items):
        # 定期显示进度
        if i % 500 == 0 and i > 0:
            elapsed = time.time() - start_time
            items_per_sec = i / elapsed if elapsed > 0 else 0
            est_remaining = (total_items - i) / items_per_sec if items_per_sec > 0 else "未知"
            print(f"处理进度: {i}/{total_items} ({i/total_items*100:.1f}%) - 速度: {items_per_sec:.1f}项/秒 - 预计剩余时间: {est_remaining:.1f}秒")
            print(f"当前内存使用: {get_memory_usage():.1f} MB")
        
        # 如果当前索引已处理，跳过
        if i in processed_indices:
            continue
        
        # 将当前索引添加为唯一项
        unique_indices.append(i)
        processed_indices.add(i)
        
        # 获取当前嵌入向量
        if isinstance(embeddings, list):
            # 找出当前索引i对应的批次和批次内索引
            current_batch_idx = 0
            cumulative_size = 0
            while current_batch_idx < len(embeddings):
                batch_size = embeddings[current_batch_idx].shape[0]
                if cumulative_size + batch_size > i:
                    break
                cumulative_size += batch_size
                current_batch_idx += 1
            
            in_batch_idx = i - cumulative_size
            current_embedding = embeddings[current_batch_idx][in_batch_idx].unsqueeze(0)
        else:
            current_embedding = embeddings[i].unsqueeze(0)  # [1, dim]
        
        # 只与尚未处理的后续项比较
        remaining_indices = [j for j in range(i + 1, total_items) if j not in processed_indices]
        
        if not remaining_indices:
            continue
        
        # 分批处理剩余索引，避免内存溢出
        for batch_start in range(0, len(remaining_indices), max_vectors_per_batch):
            batch_end = min(batch_start + max_vectors_per_batch, len(remaining_indices))
            batch_indices = remaining_indices[batch_start:batch_end]
            
            try:
                # 批量获取当前批次的嵌入向量
                if isinstance(embeddings, list):
                    batch_embeddings_list = []
                    for j in batch_indices:
                        # 找出索引j对应的批次和批次内索引
                        j_batch_idx = 0
                        j_cumulative_size = 0
                        while j_batch_idx < len(embeddings):
                            j_batch_size = embeddings[j_batch_idx].shape[0]
                            if j_cumulative_size + j_batch_size > j:
                                break
                            j_cumulative_size += j_batch_size
                            j_batch_idx += 1
                        
                        j_in_batch_idx = j - j_cumulative_size
                        batch_embeddings_list.append(embeddings[j_batch_idx][j_in_batch_idx])
                    
                    batch_embeddings = torch.stack(batch_embeddings_list)
                else:
                    batch_embeddings = embeddings[batch_indices]  # [batch_size, dim]
                
                # 计算余弦相似度矩阵 [1, batch_size]
                similarities = util.pytorch_cos_sim(current_embedding, batch_embeddings).squeeze(0)
                
                # 找出相似度高于阈值的索引
                duplicate_mask = similarities >= similarity_threshold
                duplicate_batch_indices = [idx for idx, is_duplicate in enumerate(duplicate_mask) if is_duplicate]
                duplicate_indices = [batch_indices[idx] for idx in duplicate_batch_indices]
                
                # 将重复项添加到已处理集合
                processed_indices.update(duplicate_indices)
                
            except Exception as e:
                print(f"处理批次 {batch_start}-{batch_end} 时出错: {str(e)}")
                print("跳过当前批次，继续处理下一个...")
                continue
        
        # 定期执行垃圾回收
        if i > 0 and i % 1000 == 0:
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
    
    return unique_indices

def semantic_deduplication(data, model_name='all-MiniLM-L6-v2', similarity_threshold=0.95, batch_size=32, max_vectors_per_batch=100):
    """
    执行语义去重，使用优化的PyTorch实现
    
    Args:
        data: 要去重的数据项列表
        model_name: 用于嵌入的SentenceTransformer模型
        similarity_threshold: 视为重复项的相似度阈值 (0.0-1.0)
        batch_size: 处理批次大小（较小的值使用更少内存但速度较慢）
        max_vectors_per_batch: 相似度计算时每批次的最大向量数
    
    Returns:
        去重后的数据项列表
    """
    start_time = time.time()
    print(f"开始语义去重，使用模型 {model_name}，相似度阈值 {similarity_threshold}")
    
    if not data:
        return []
    
    # 监控内存使用
    print(f"初始内存使用: {get_memory_usage():.1f} MB")
    
    try:
        # 加载模型
        print("加载Sentence Transformer模型...")
        model = SentenceTransformer(model_name)
        
        # 准备文本
        print("准备文本数据...")
        texts_to_embed = prepare_texts(data)
        print(f"共 {len(texts_to_embed)} 个问答对需要处理")
        
        # 生成嵌入向量
        print("生成嵌入向量...")
        print(f"嵌入前内存使用: {get_memory_usage():.1f} MB")
        
        # 使用较小的批次大小生成嵌入向量
        embeddings = batch_encode_texts(model, texts_to_embed, batch_size=batch_size)
        
        # 清理不再需要的文本数据
        del texts_to_embed
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        print(f"嵌入后内存使用: {get_memory_usage():.1f} MB")
        
        # 查找重复项
        print("使用PyTorch批量矩阵操作查找重复项...")
        unique_indices = find_duplicates_with_pytorch(
            embeddings, 
            similarity_threshold=similarity_threshold,
            max_vectors_per_batch=max_vectors_per_batch
        )
        
        # 构建去重后的数据集
        deduplicated_data = [data[i] for i in unique_indices]
        
        # 打印统计信息
        elapsed_time = time.time() - start_time
        print(f"语义去重完成。原始: {len(data)}，去重后: {len(deduplicated_data)} 个问答对。")
        print(f"处理时间: {elapsed_time:.2f}秒，平均速度: {len(data)/elapsed_time:.1f}项/秒")
        print(f"去重率: {(1 - len(deduplicated_data)/len(data))*100:.1f}%")
        print(f"最终内存使用: {get_memory_usage():.1f} MB")
        
        return deduplicated_data
        
    except Exception as e:
        print(f"语义去重过程中出错: {str(e)}")
        traceback.print_exc()
        print("返回原始数据，不执行去重")
        return data

def filter_by_keywords(data, keywords):
    """Filters Q&A pairs based on the presence of keywords in prompt or response."""
    filtered_data = []
    for item in data:
        prompt_text = item.get('prompt', '')
        response_list = item.get('response', [])
        # The response is a list of lists, e.g., [["summary sentence"]]
        # We need to join the strings if they are in nested lists.
        response_text = ''
        if response_list and isinstance(response_list, list):
            for sub_list in response_list:
                if isinstance(sub_list, list):
                    response_text += ' '.join(str(s) for s in sub_list) + ' '
                else:
                    response_text += str(sub_list) + ' '
        
        text_to_search = (prompt_text + ' ' + response_text.strip()).lower()
        if any(keyword in text_to_search for keyword in keywords):
            filtered_data.append(item)
    return filtered_data

def main():
    # 加载原始数据
    print(f"从 {INPUT_FILE} 加载数据...")
    original_data = load_jsonl(INPUT_FILE)
    print(f"已加载 {len(original_data)} 个问答对。")

    # 步骤 1.1: 语义去重 - 使用优化的PyTorch实现
    try:
        print("使用优化的PyTorch实现进行语义去重...")
        deduplicated_data = semantic_deduplication(
            original_data,
            similarity_threshold=0.95,  # 相似度阈值
            batch_size=32,             # 编码批次大小（较小值减少内存使用）
            max_vectors_per_batch=50   # 相似度计算时每批次的最大向量数
        )
        save_jsonl(deduplicated_data, DEDUPLICATED_FILE)
    except Exception as e:
        print(f"语义去重失败: {str(e)}")
        print("跳过去重步骤，使用原始数据继续...")
        deduplicated_data = original_data

    # Step 1.2: Keyword Filtering
    print("\n步骤 1.2: 按关键词过滤...")
    
    # Filter for Log/Observability related data
    log_related_data = filter_by_keywords(deduplicated_data, LOG_KEYWORDS)
    save_jsonl(log_related_data, LOG_RELATED_FILE)
    print(f"过滤出 {len(log_related_data)} 个日志/可观测性相关的问答对。")

    # Filter for CI/CD/General Programming related data
    cicd_related_data = filter_by_keywords(deduplicated_data, CI_CD_KEYWORDS)
    save_jsonl(cicd_related_data, CICD_RELATED_FILE)
    print(f"过滤出 {len(cicd_related_data)} 个CI/CD和通用编程相关的问答对。")

    print("\n数据预处理完成。")

if __name__ == '__main__':
    main()