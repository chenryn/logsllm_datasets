#!python3
import os
import glob
import re
from math import ceil
from tiktoken import get_encoding

# 获取文件的 encoding
encoding = get_encoding("cl100k_base")

def split_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:  # 使用正确的 encoding
        text = file.read()
        tokens = encoding.encode(text, disallowed_special=())
        lens = len(tokens)
        if lens > 4096:
            split_count = ceil(lens / 4096)
            line = text.split('\n')
            lines = ceil( len(line) / split_count )
            print(f"split -l {lines} \"{filepath}\" \"{filepath}_\" || echo -ne \"{filepath}\"")
        else:
            print(f"mv \"{filepath}\" small/{filepath}.txt")

def split_md(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:  # 使用正确的 encoding
        text = file.read()
        tokens = encoding.encode(text)
        lens = len(tokens)
        if lens > 4096:
            split_count = ceil(lens / 4096)
            print(f"mkdir -p markdown/{split_count}/res; mv \"{filepath}\" \"{split_count}/{filepath}\" ")
        else:
            print(f"mv \"{filepath}\" small/{filepath}.txt")

# 遍历目录下的所有 txt 文件
for filepath in glob.glob('postmortem/md/*'):
#    split_file(filepath)
    split_md(filepath)

