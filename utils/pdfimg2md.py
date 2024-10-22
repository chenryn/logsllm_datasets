#!python3

import pdf2image
from PIL import Image
import pytesseract
import os
import sys

def pdf_to_md(pdf_file, output_md):
    # Convert PDF to list of images
    images = pdf2image.convert_from_path(pdf_file)

    # Initialize markdown file
    with open(output_md, 'w') as f:
        f.write('# OCR Output\n\n')

    # OCR each image and write to markdown file
    for i, image in enumerate(images):
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')  # 使用中文和英文识别
        with open(output_md, 'a') as f:
            f.write(f'## Page {i+1}\n\n')
            f.write(text)
            f.write('\n\n---\n\n')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        output_md = pdf_file.replace('.pdf', '.md')
        pdf_to_md(pdf_file, output_md)
    else:
        print('未提供pdf')

