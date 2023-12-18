import re
import openpyxl
import xml.etree.ElementTree as ET

def txt_to_excel(txt_file):

    try:
        # 使用utf-8编码读取txt文件
        with open(txt_file, encoding='utf-8') as f:
            text = f.read()

    except UnicodeDecodeError:
        # 解码错误时,忽略错误读取
        with open(txt_file, 'r', errors='ignore') as f:
            text = f.read()

    # 使用正则表达式提取XML字符串
    pattern = re.compile(r'<message>.*</message>', re.DOTALL)
    xml_str = re.search(pattern, text).group()

    # 解析XML
    root = ET.fromstring(xml_str)

    headers = []
    for child in root.iter():

        parts = child.tag.split('}')
        if len(parts) > 1:
            tag = parts[1]
        else:
            tag = parts[0]

        if tag not in headers:
            headers.append(tag)


    # 提取数据
    results = []
    for child in root:
        data = []
        for header in headers:
            element = child.find(header)
            if element is not None:
                data.append(element.text)
            else:
                data.append('')
        results.append(data)

    # 写入Excel
    wb = openpyxl.Workbook()
    sheet = wb.active

    sheet.append(headers)

    for row in results:
        sheet.append(row)

    wb.save('data2.xlsx')

txt_to_excel('data2.txt')