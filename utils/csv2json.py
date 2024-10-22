#!python3
import csv
import json

# 假设CSV文件的路径是 'example.csv'
csv_file_path = 'KQL.csv'
# 假设我们想要保存JSON到的文件路径是 'output.json'
json_file_path = 'output.json'

# 创建一个空列表来存储所有的JSON对象
json_list = []

# 打开CSV文件并读取
with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
    # 使用csv.DictReader来读取CSV文件
    reader = csv.DictReader(csvfile)
    # 遍历CSV文件的每一行
    for row in reader:
        json_list.append(json.dumps(row, ensure_ascii=False))

# 将JSON列表写入到文件中
with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
    # 将每个JSON对象写入文件，并确保每个对象占一行
    for json_obj in json_list:
        jsonfile.write(json_obj + '\n')

print(f'转换完成，结果保存在 {json_file_path}')

