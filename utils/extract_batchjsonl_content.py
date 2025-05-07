#!/usr/bin/env python3
import json
import os
import glob
import re

def extract_content_from_jsonl(jsonl_file_path):
    """从JSONL文件中提取内容并保存为txt文件"""
    print(f"处理文件: {jsonl_file_path}")
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(jsonl_file_path), "extracted_content_2")
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取JSONL文件并处理每一行
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                # 解析JSON对象
                json_obj = json.loads(line)
                
                # 提取custom_id作为文件名
                if 'custom_id' in json_obj:
                    custom_id = json_obj['custom_id']
                    # 从custom_id中提取文件名部分（格式如：request-filter2aa_3343_aa.txt-37964125）
                    pattern = r'^request-(?P<filename>.*?.txt)-\S{8}$'
                    match = re.match(pattern, custom_id)
                    if match:
                        # 使用正则命名组提取文件名
                        filename = match.group('filename')
                    else:
                        # 如果格式不符合预期，使用整个custom_id
                        filename = custom_id
                else:
                    # 如果没有custom_id，使用行号作为文件名
                    filename = f"line_{line_num}.txt"
                
                # 提取content内容
                if 'response' in json_obj and 'body' in json_obj['response']:
                    body = json_obj['response']['body']
                    if 'choices' in body and len(body['choices']) > 0:
                        if 'message' in body['choices'][0] and 'content' in body['choices'][0]['message']:
                            content = body['choices'][0]['message']['content']
                            
                            # 保存内容到txt文件
                            output_file = os.path.join(output_dir, f"{filename}")
                            with open(output_file, 'w', encoding='utf-8') as out_f:
                                out_f.write(content)
                            print(f"已保存内容到: {output_file}")
                        else:
                            print(f"行 {line_num}: 未找到message.content")
                    else:
                        print(f"行 {line_num}: 未找到choices或choices为空")
                else:
                    print(f"行 {line_num}: 未找到response.body")
            except json.JSONDecodeError:
                print(f"行 {line_num}: JSON解析错误")
            except Exception as e:
                print(f"行 {line_num}: 处理错误 - {str(e)}")

def main():
    # 查找data/pretrain目录下的所有_success.jsonl文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pretrain_dir = os.path.join(base_dir, "data", "pretrain")
    jsonl_files = glob.glob(os.path.join(pretrain_dir, "*_success.jsonl"))
    
    if not jsonl_files:
        print(f"在 {pretrain_dir} 目录下未找到_success.jsonl文件")
        return
    
    print(f"找到 {len(jsonl_files)} 个JSONL文件")
    
    # 处理每个JSONL文件
    for jsonl_file in jsonl_files:
        extract_content_from_jsonl(jsonl_file)
    
    print("处理完成!")

def compare_and_clean_dirs(dir1, dir2):
    """比较两个目录中的同名文件，保留dir1下的文件并删除dir2下的对应文件"""
    print(f"比较目录: {dir1} 和 {dir2}")
    
    # 获取两个目录中的所有文件名
    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))
    
    # 找出重复的文件名
    duplicate_files = files1 & files2
    
    if not duplicate_files:
        print("没有找到重复的文件名")
        return
    
    print(f"找到 {len(duplicate_files)} 个重复文件")
    
    # 删除dir2中的重复文件
    for filename in duplicate_files:
        file_path = os.path.join(dir2, filename)
        try:
            os.remove(file_path)
            print(f"已删除: {file_path}")
        except Exception as e:
            print(f"删除 {file_path} 失败: {str(e)}")

if __name__ == "__main__":
    #main()
    
    # 比较并清理目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    extracted_dir = os.path.join(base_dir, "data", "pretrain", "extracted_content_2")
    low_txt_dir = os.path.join(base_dir, "data", "pretrain", "low_txt")
    
    if os.path.exists(extracted_dir) and os.path.exists(low_txt_dir):
        compare_and_clean_dirs(extracted_dir, low_txt_dir)