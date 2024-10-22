#!python3
# coding=utf-8

import os
import sys
from multiprocessing import Pool, cpu_count
import numpy as np

# 设置环境变量
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 导入transformers库
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# 初始化模型和分词器
model = GPT2LMHeadModel.from_pretrained('gpt2')
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
max_length = 340

# 定义一个函数来计算单个块的困惑度
def compute_perplexity(block):
    input_ids = tokenizer.encode(block, return_tensors='pt')
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        loss = outputs[0]
        perplexity = torch.exp(loss)
    return perplexity.item()

if __name__ == "__main__":
    # 检查是否提供了文件名
    if len(sys.argv) > 1:
        # 获取第一个参数（索引0是脚本名称）
        filename = sys.argv[1]
        # 读取文本文件
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        # 将文本分块
        blocks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        
        # 使用所有可用的CPU核心
        # num_cpus = cpu_count()
        pool = Pool(4)

        # 并行计算每个块的困惑度
        perplexities = pool.map(compute_perplexity, blocks)
        # 关闭进程池
        pool.close()
        pool.join()
        # 计算平均困惑度
        average_perplexity = np.mean(perplexities)
        print(f'The average perplexity of {filename} is: {average_perplexity}')
    else:
        print('未提供文件名。')
