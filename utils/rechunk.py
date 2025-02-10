#!python
import os
import json
from typing import List, Dict
import zhipuai

# 配置智谱AI密钥
zhipuai.api_key = "YOUR_API_KEY"

def read_original_files(input_dir: str) -> Dict[str, List[str]]:
    """读取原始的按页切分的文件"""
    documents = {}
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            doc_name = filename.split('_page_')[0]
            if doc_name not in documents:
                documents[doc_name] = []
            
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                documents[doc_name].append(content)
    
    return documents

def merge_pages(pages: List[str]) -> str:
    """合并页面内容，移除页码标记"""
    merged_content = ""
    for page in pages:
        # 移除 "### 页码" 格式的标记
        content = page.replace(r'###\s+\d+\s*\n', '', regex=True)
        merged_content += content + "\n"
    return merged_content.strip()

def split_by_semantics(content: str, max_size: int = 4000) -> List[str]:
    """使用大模型API来进行语义切分"""
    prompt = f"""请将以下文本切分成多个部分，要求：
1. 每部分不超过4000字节
2. 切分时要考虑语义完整性，尽量在自然段落或章节处切分
3. 返回JSON格式，格式为: {{"splits": ["部分1", "部分2", ...]}}

文本内容：
{content}
"""
    
    response = zhipuai.model_api.invoke(
        model="chatglm_pro",
        prompt=prompt,
        temperature=0.1,
        top_p=0.7,
    )
    
    try:
        result = json.loads(response['data']['choices'][0]['content'])
        return result['splits']
    except:
        # 如果API调用失败或解析失败，使用简单的长度切分作为后备方案
        return [content[i:i+max_size] for i in range(0, len(content), max_size)]

def save_splits(doc_name: str, splits: List[str], output_dir: str):
    """保存切分后的文件"""
    os.makedirs(output_dir, exist_ok=True)
    for i, content in enumerate(splits):
        filename = f"{doc_name}_part_{i+1}.txt"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    input_dir = "../data/raw"  # 原始数据目录
    output_dir = "../data/optimized"  # 优化后的输出目录
    
    # 读取原始文件
    documents = read_original_files(input_dir)
    
    # 处理每个文档
    for doc_name, pages in documents.items():
        print(f"Processing document: {doc_name}")
        
        # 合并页面
        merged_content = merge_pages(pages)
        
        # 语义切分
        splits = split_by_semantics(merged_content)
        
        # 保存结果
        save_splits(doc_name, splits, output_dir)
        print(f"Finished processing {doc_name}, generated {len(splits)} parts")

if __name__ == "__main__":
    main()
