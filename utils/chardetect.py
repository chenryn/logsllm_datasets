import os
import chardet
import shutil

# 遍历当前目录下的所有文件
for filename in os.listdir('.'):
    if filename.endswith('.txt') and os.path.isfile(filename):
        # 读取文件内容
        with open(filename, 'rb') as file:
            content = file.read()
            # 检测文件编码
            encoding_result = chardet.detect(content)
            encoding = encoding_result['encoding']
            confidence = encoding_result['confidence']
            
            # 如果编码检测的置信度足够高，并且编码不是UTF-8，则转换文件
            if confidence > 0.9 and encoding is not None and encoding.upper() not in ['UTF-8', 'ASCII']:
                # 备份原始文件
                backup_filename = filename + '.bak'
                shutil.copy2(filename, backup_filename)
                print(f"文件 {filename} 已备份为 {backup_filename}。")
                
                # 使用检测到的编码读取文件内容
                with open(filename, 'r', encoding=encoding, errors='ignore') as file:
                    text = file.read()
                
                # 使用UTF-8编码写入文件内容
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(text)
                
                print(f"文件 {filename} 已从 {encoding} 转换为 UTF-8。")

