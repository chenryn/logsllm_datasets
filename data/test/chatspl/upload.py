#!python3
import glob
import json
import requests

def send_json_to_server(json_data, url):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.put(url, headers=headers, json=json_data)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Request Error: {e}"

def process_files(directory, server_url):
    for filename in glob.glob(f"{directory}/*.json"):
        with open(filename, 'r', encoding='utf-8') as file:  # 使用 utf-8 编码打开文件
            for line in file:
                try:
                    json_data = json.loads(line)
                    response = send_json_to_server(json_data, server_url)
                    if response['rc'] != 0:
                        print(response)  # 打印请求错误信息
                    else:
                        print(f"Sent data from {filename}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in {filename}: {e}")

# 替换为您的 JSON 文件所在目录的路径
# 以及您的服务器 URL
process_files('/Users/rizhiyi/Downloads/gitdir/logsllm_datasets/data/test/chatspl/raw', 'http://192.168.40.109:9400/_beaver')
