#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import uuid
import math

# 定义输入和输出路径
input_dir = "/Users/rizhiyi/Downloads/logsllm_datasets/data/pretrain/low_txt/"
output_dir = "/Users/rizhiyi/Downloads/logsllm_datasets/data/pretrain/"

# 批处理设置
MAX_REQUESTS_PER_BATCH = 50000

# 系统提示信息
system_prompt = "你是文本质量优化助手，请帮我优化以下文本，使其更加清晰、连贯和专业。"

def create_jsonl_record(file_name, content):
    """创建JSONL格式的记录"""
    # 创建唯一ID
    custom_id = f"request-{file_name}-{str(uuid.uuid4())[:8]}"
    
    # 创建JSONL格式的记录
    record = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "qwen-max",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        }
    }
    return record

def convert_files_to_jsonl():
    """将文本文件转换为批量推理所需的JSONL格式，并分批处理"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有文本文件
    text_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    total_files = len(text_files)
    
    # 计算需要多少批次
    num_batches = math.ceil(total_files / MAX_REQUESTS_PER_BATCH)
    print(f"总共有 {total_files} 个文件，将分成 {num_batches} 个批次处理")
    
    # 处理每个批次
    for batch_num in range(num_batches):
        # 计算当前批次的文件范围
        start_idx = batch_num * MAX_REQUESTS_PER_BATCH
        end_idx = min((batch_num + 1) * MAX_REQUESTS_PER_BATCH, total_files)
        batch_files = text_files[start_idx:end_idx]
        
        # 创建批次输出文件
        output_file = os.path.join(output_dir, f"batch_inference_{batch_num + 1}.jsonl")
        
        # 打开输出文件
        with open(output_file, 'w', encoding='utf-8') as out_f:
            # 处理当前批次的每个文本文件
            for i, file_name in enumerate(batch_files):
                file_path = os.path.join(input_dir, file_name)
                
                try:
                    # 读取文本文件内容
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().strip()
                    
                    # 如果内容为空，跳过该文件
                    if not content:
                        print(f"跳过空文件: {file_name}")
                        continue
                    
                    # 创建并写入JSONL记录
                    record = create_jsonl_record(file_name, content)
                    out_f.write(json.dumps(record, ensure_ascii=False) + '\n')
                    
                    # 打印进度
                    global_index = start_idx + i + 1
                    if (i + 1) % 50 == 0 or (i + 1) == len(batch_files):
                        print(f"批次 {batch_num + 1}: 已处理 {i + 1}/{len(batch_files)} 个文件 (总进度: {global_index}/{total_files})")
                        
                except Exception as e:
                    print(f"处理文件 {file_name} 时出错: {str(e)}")
        
        print(f"批次 {batch_num + 1} 处理完成! 输出文件: {output_file}")
    
    print(f"\n所有批次处理完成!")
    print(f"共处理了 {total_files} 个文本文件，分成了 {num_batches} 个批次")

if __name__ == "__main__":
    convert_files_to_jsonl()