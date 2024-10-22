#!python3
import argparse
import pandas as pd

def parquet_to_md(parquet_path, json_path):
    print(parquet_path, json_path)
    # 读取 parquet 文件
    df = pd.read_parquet(parquet_path)
    # 将 DataFrame 保存为 json 文件
    df.to_json(json_path, orient='records', force_ascii=False)

parser = argparse.ArgumentParser()
parser.add_argument('--parquet_path', help='path to the parquet file')
args = parser.parse_args()

parquet_path = args.parquet_path 
json_path = parquet_path.replace('.parquet', '.json')
md = parquet_to_md(parquet_path, json_path)

