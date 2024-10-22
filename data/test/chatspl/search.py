#!python3
import json
import requests
import urllib.parse

def send_request(command, now, start_ts):
    encoded_command = urllib.parse.quote(command)
    url = f"http://192.168.40.109:9400/spl/jobs/search?domain_name=ops&user_id=1&task_name=search_task&pipe_command={encoded_command}&datasets=[%22tag%3Achatspl%22]&start_ts={start_ts}/d&end_ts=now&now={now}&query_sort_by_fields=&background=false&timeline=false&statsevents=false&fields=false&highlight=false&test_mode=false&sort=desc&category=search&from=0&size=1000&terminated_after_size=&timeout=60000&use_spark=&lang=zh_CN"
    response = requests.get(url)
    return response.json()

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                data = json.loads(line)
                print(data['now'],data['output'],data['start_ts'])
                response = send_request(data['output'], data['now'], data['start_ts'])
                if response['rc'] != 0:
                    print(json.dumps(response, ensure_ascii=False))
                else:
                    if response['result']['type'] == 'query':
                        print(response['result']['total_hits'])
                    elif response['result']['type'] == 'stats':
                        print(response['result']['total_hits'], response['result']['sheets']['total'])
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except requests.exceptions.RequestException as e:
                print(f"HTTP Request Error: {e}")

# 替换为您的文件名
process_file('test.json')
