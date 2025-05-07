from huggingface_hub import hf_hub_download
import fasttext
import os
import yaml
import re
import argparse

# 全局变量，用于存储加载的模型
_MODEL = None

def load_model():
    """加载模型，只需执行一次"""
    global _MODEL
    if _MODEL is None:
        # 下载模型
        model_path = hf_hub_download(
            repo_id="mlfoundations/fasttext-oh-eli5",
            filename="openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin"
        )
        # 加载模型
        _MODEL = fasttext.load_model(model_path)
    return _MODEL

def get_model_score(text):
    # 获取模型（如果尚未加载，则会加载）
    model = load_model()
    
    # 预处理文本：移除多余空白并合并成单行
    text = ' '.join(text.strip().splitlines())

    # 预测
    predictions = model.predict(text, k=2)
    labels = predictions[0]
    probabilities = predictions[1]

    # 获取预测标签和概率
    pred_label = labels[0]
    pred_prob = probabilities[0]

    # 如果预测为 cc (低质量)，则概率需要反转
    if pred_label == '__label__cc':
        pred_prob = 1 - pred_prob

    return pred_label, pred_prob

def read_markdown_content(file_path):
    """读取 markdown 文件的标题和内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 分离 YAML front matter 和正文内容
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    if isinstance(front_matter, dict):  # 确保front_matter是字典
                        title = front_matter.get('title', '')
                        body = parts[2].strip()
                        return title, body
                    return '', content  # 如果不是字典，返回空标题和完整内容
                except yaml.YAMLError:
                    return '', content
        return '', content  # 对于纯文本文件，返回空标题和完整内容
    except UnicodeDecodeError:
        # 如果 UTF-8 解码失败，尝试使用 GB2312
        with open(file_path, 'r', encoding='gb2312') as f:
            content = f.read()
            
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    title = front_matter.get('title', '')
                    body = parts[2].strip()
                    return title, body
                except yaml.YAMLError:
                    return '', content
        return '', content
    
def process_files(threshold=0.018112, specific_file=None, directory=None, output_file=None):
    """
    处理文件并评估质量
    :param threshold: 质量评分阈值
    :param specific_file: 指定要处理的单个文件路径
    :param directory: 指定要处理的目录路径
    :param output_file: 不达标文件名输出文件路径
    :return: 处理结果列表
    """
    # 默认目录
    default_dir = '/Users/rizhiyi/Downloads/logsllm_datasets/data/pretrain/LogGPTV2_20240403_110829'
    # 使用指定目录或默认目录
    files_dir = directory if directory else default_dir
    results = []
    
    # 准备输出文件
    output_f = None
    if output_file:
        # 使用 'w' 模式打开文件，如果文件已存在则清空内容
        try:
            output_f = open(output_file, 'w', encoding='utf-8')
        except IOError as e:
            print(f"错误：无法打开输出文件 '{output_file}': {e}")
            output_file = None # 禁用输出文件功能
    
    try:
        # 如果指定了特定文件
        if specific_file:
            # 检查是否提供了完整路径
            if os.path.isfile(specific_file):
                file_path = specific_file
            else:
                # 尝试在files_dir目录下查找
                file_path = os.path.join(files_dir, specific_file)
            
            if os.path.isfile(file_path):
                _, content = read_markdown_content(file_path)
                label, score = get_model_score(content)
                
                results.append({
                    'file': os.path.relpath(file_path, files_dir) if file_path.startswith(files_dir) else os.path.basename(file_path),
                    'label': label,
                    'score': score,
                    'passed_threshold': score >= threshold
                })
                
                # 如果指定了输出文件且文件未通过阈值，则写入文件名
                if output_f and not (score >= threshold):
                    output_f.write(os.path.basename(file_path) + '\n')
            else:
                print(f"错误：找不到指定的文件 '{specific_file}'")
                return []
        else:
            # 处理目录中的所有文件
            all_files = []
            if os.path.isdir(files_dir):
                all_files = [entry for entry in os.scandir(files_dir) if entry.is_file() and entry.name.endswith('.txt')]
            else:
                print(f"错误：找不到指定的目录 '{files_dir}'")
                return []
                
            total_files = len(all_files)
            processed_count = 0
            print(f"开始处理 {total_files} 个文件...")

            # 处理所有文件
            for entry in all_files:
                filename = entry.name
                file_path = entry.path
                processed_count += 1
                if processed_count % 100 == 0 or processed_count == total_files:
                    print(f"已处理 {processed_count}/{total_files} 个文件 ({processed_count/total_files*100:.2f}%)")
                
                try:
                    # 读取文件内容
                    _, content = read_markdown_content(file_path)
                    
                    # 获取文件评分和标签
                    label, score = get_model_score(content)
                    
                    result_item = {
                        'file': filename,
                        'label': label,
                        'score': score,
                        'passed_threshold': score >= threshold
                    }
                    results.append(result_item)
                    
                    # 如果指定了输出文件且文件未通过阈值，则立即写入文件名
                    if output_f and not result_item['passed_threshold']:
                        output_f.write(filename + '\n')
                        
                except Exception as e:
                    print(f"处理文件 {filename} 时出错: {e}")
                    # 将错误信息添加到结果中
                    result_item = {
                        'file': filename,
                        'label': 'Error',
                        'score': 0.0,
                        'passed_threshold': False,
                        'error': str(e)
                    }
                    results.append(result_item)
                    # 如果指定了输出文件，也将处理出错的文件名写入
                    if output_f:
                        output_f.write(filename + '\n')
    finally:
        # 确保输出文件被关闭
        if output_f:
            output_f.close()
    
    # 按评分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

if __name__ == '__main__':
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='评估文件质量')
    parser.add_argument('-f', '--file', help='指定要评估的特定文件路径')
    parser.add_argument('-d', '--directory', help='指定要评估的目录路径')
    parser.add_argument('-t', '--threshold', type=float, default=0.018112, 
                        help='质量评分阈值（默认：0.018112）')
    parser.add_argument('-o', '--output', help='不达标文件名输出文件路径')
    args = parser.parse_args()
    
    # 检查参数
    if args.file and args.directory:
        print("错误：不能同时指定文件(-f)和目录(-d)参数")
        exit(1)
    
    # 处理文件
    results = process_files(
        threshold=args.threshold, 
        specific_file=args.file, 
        directory=args.directory,
        output_file=args.output
    )
    
    if not results:
        exit()
    
    # 统计信息
    total_files = len(results)
    passed_files = sum(1 for r in results if r['passed_threshold'])
    
    print("\n文件质量评分结果：")
    print(f"总文件数: {total_files}")
    print(f"通过质量阈值的文件数: {passed_files}")
    print(f"通过率: {(passed_files/total_files*100):.2f}%" if total_files > 0 else "N/A")
    print("-" * 60)
    
    # 打印每个文件的详细信息
    for item in results:
        print(f"文件: {item['file']}")
        print(f"标签: {item['label']}")
        print(f"评分: {item['score']:.3f}")
        print(f"是否通过阈值: {'是' if item['passed_threshold'] else '否'}")
        if 'error' in item:
            print(f"错误: {item['error']}")
        print("-" * 60)
    
    # 不合格文件名已在 process_files 中实时写入，此处无需操作
    if args.output:
        print(f"\n不合格的文件名已写入到: {args.output}")