#!python3
import argparse
import pandas as pd
import json

def convert_obj(obj):
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except ImportError:
        pass
    if isinstance(obj, dict):
        return {k: convert_obj(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_obj(item) for item in obj]
    else:
        return obj


def parquet_to_md(parquet_path, json_path):
    print(parquet_path, json_path)
    # 读取 parquet 文件
    df = pd.read_parquet(parquet_path)
    # 将 DataFrame 每行写为一行 JSON object
    with open(json_path, 'w', encoding='utf-8') as f:
        for record in df.to_dict(orient='records'):
            record = convert_obj(record)
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--parquet_path', help='path to the parquet file')
    args = parser.parse_args()

    parquet_path = args.parquet_path 
    json_path = parquet_path.replace('.parquet', '.json')
    md = parquet_to_md(parquet_path, json_path)


