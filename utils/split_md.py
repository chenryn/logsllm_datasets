#!python3
import os
import sys
from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class SectionSplitter(Extension):
    def __init__(self, split_count):
        self.split_count = split_count
        self.current_part = 0
        self.part_files = [[] for _ in range(split_count)]
        self.current_line_count = 0
        self.lines_per_part = 0
        self.total_lines = 0

    def extendMarkdown(self, md):
        md.preprocessors.register(self, 'sections', 35)

    def run(self, lines):
        self.total_lines += len(lines)
        self.lines_per_part = self.total_lines // self.split_count

        for line in lines:
            self.current_line_count += 1
            if self.current_line_count > self.lines_per_part and self.current_part < self.split_count - 1:
                self.current_part += 1
                self.current_line_count = 1
            self.part_files[self.current_part].append(line+"\n")
        return []


def split_markdown_files(split_count):
    for filename in os.listdir('.'):
        if filename.endswith('.md'):
            md = Markdown(extensions=[SectionSplitter(split_count)])
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                md.convert("".join(lines))
            base_filename, _ = os.path.splitext(filename)
            for i, part in enumerate(md.preprocessors['sections'].part_files):
                if part:  # Only write if the part is not empty
                    output_filename = f"res/{base_filename}_part_{i+1}.txt"
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        f.writelines(part)

# 检查是否有足够的命令行参数
if len(sys.argv) > 1:
    # 获取第一个参数（索引0是脚本名称）
    split_count = sys.argv[1]
    # 尝试将参数转换为整数
    try:
        split_count = int(split_count)
        split_markdown_files(split_count)
    except ValueError:
        print('提供的参数不是有效的整数。')
else:
    print('未提供目标令牌计数。')


