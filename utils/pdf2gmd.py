#!python3.11
import argparse
import pdfplumber
import camelot
import pandas as pd
from tabulate import tabulate

def pdf_to_md(pdf_path):
    
    # 提取文本 
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
    text = '\n\n'.join(pages)
    
    # 提取表格
    tables = camelot.read_pdf(pdf_path)
    df_list = [table.df for table in tables]
    
    # 渲染表格为 markdown 格式 
    markdown_tables = [tabulate(df, tablefmt='github') for df in df_list]
    
    # 把文本和表格组合
    md = '\n'.join([text] + markdown_tables)

    return md

parser = argparse.ArgumentParser()
parser.add_argument('--pdf_path', help='path to the pdf file')
args = parser.parse_args()

pdf_path = args.pdf_path 
md = pdf_to_md(pdf_path)

md_path = pdf_path.replace('.pdf', '.md')
with open(md_path, 'w') as f:
    f.write(md)

