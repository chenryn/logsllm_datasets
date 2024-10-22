#!python3.11
import sys
import fitz  # PyMuPDF
from paddleocr import PaddleOCR, draw_ocr
import numpy as np
import os

def pdf_to_md(pdf_file, output_md):
    # 打开PDF文件
    pdf = fitz.open(pdf_file)
    print("PDF opened")

    # Initialize markdown file
    with open(output_md, 'w') as f:
        f.write('# OCR Output\n\n')

    # Initialize PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang='ch', log_level='error')  # 使用中文识别

    # OCR each page and write to markdown file
    for i in range(len(pdf)):
        page = pdf[i]
        # 将PDF页面转换为图片
        pix = page.get_pixmap()
        width, height = pix.width, pix.height
        if pix.n >= 4:  # 如果是CMYK或带有alpha通道的图像
            # 将CMYK转换为RGB
            image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(height, width, pix.n)
        else:  # 对于RGB图像
            # 直接将像素数据转换为NumPy数组
            image_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(height, width, pix.n)

        result = ocr.ocr(image_np, cls=True)
        # Extract text from OCR result
        if result is not None and result[0] is not None:
            text = []
            for line in result[0]:
                if line is not None and isinstance(line, list) and len(line) > 1:
                    text.append(line[1][0])
        
            with open(output_md, 'a') as f:
                f.write(f'## Page {i+1}\n\n')
                f.write('\n'.join(text))
                f.write('\n\n---\n\n')

    # Close the PDF file
    pdf.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        output_md = pdf_file.replace('.pdf', '.md')
        pdf_to_md(pdf_file, output_md)
    else:
        print('未提供pdf')

