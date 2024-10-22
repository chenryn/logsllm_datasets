import os
import simhash
from simhash import Simhash

# 设置相似度阈值，可以根据实际情况进行调整
SIMILARITY_THRESHOLD = 0.8

# 存储文件内容的 simhash 值和文件路径
file_simhash = {}

# 遍历当前目录下的所有文件
for filename in os.listdir('.'):
    if os.path.isfile(filename):
        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 计算文件的 simhash 值
        file_simhash[filename] = Simhash(content)
        print(f"{filename} calc ok.")

# 比对文件内容的 simhash 值，删除重复率过高的文件
deleted_files = []
for i, file1 in enumerate(file_simhash):
    for file2 in list(file_simhash)[i+1:]:
        # 计算两个文件的 simhash 值的相似度
        similarity = file_simhash[file1].distance(file_simhash[file2])

        # 如果相似度超过阈值，删除其中一个文件
        if similarity < SIMILARITY_THRESHOLD:
            deleted_files.append(file2)
        print(f"{file1} {file2} calc ok.")
#            os.remove(file2)

# 输出被删除的文件列表
print("Deleted files:", deleted_files)

