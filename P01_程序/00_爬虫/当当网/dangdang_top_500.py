# Encoding: UTF-8
import os
import requests
import re
import json

import xlsxwriter

from openpyxl import Workbook, load_workbook



# 获取当当网图书销量前500的图书信息
def request_dandan(url):
    try:
        response = requests.get(url)            # 伪装成浏览器
        if response.status_code == 200:             # 判断是否请求成功
            return response.text                    # 返回网页源码
    except requests.RequestException as e:      # 捕获异常
        print(e)                                # 打印异常信息
        return None

# 解析网页源码
def parse_result(html):
    # 正则表达式 .*? 代表匹配任意字符 获取我们想要的信息
    pattern = re.compile(
        '<li.*?list_num.*?(\d+)\.</div>.*?<img src="(.*?)".*?class="name".*?title="(.*?)">.*?class="star">.*?class="tuijian">(.*?)</span>.*?class="publisher_info">.*?target="_blank">(.*?)</a>.*?class="biaosheng">.*?<span>(.*?)</span></div>.*?<p><span class="price_n">(.*?)</span>.*?</li>', re.S)
    items = re.findall(pattern, html)       # 匹配所有符合规则的内容

    # 遍历列表
    for item in items:
        yield {
            'range': item[0],               # 序号
            'image': item[1],               # 图片
            'title': item[2],               # 标题
            'recommend': item[3],           # 推荐语
            'author': item[4],              # 作者
            'times': item[5],               # 出版时间
            'price': item[6]                # 价格
        }

# 写入文件
def write_item_to_file(item):
    print('开始写入数据 ====> ' + str(item))
    with open('book.txt', 'a', encoding='UTF-8') as f:              # a 表示追加写入文件中
        f.write(json.dumps(item, ensure_ascii=False) + '\n')            # json.dumps()将字典形式的数据转化为字符串

# 主函数
def main(page):
    url = 'http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-' + str(page)  # 构造url
    html = request_dandan(url)                                                                      # 请求网页并返回源码
    items = parse_result(html)  # 解析过滤我们想要的信息
    for item in items:
        # write_item_to_file(item)
        write_dict_to_excel(item, 'book.xlsx')



if __name__ == "__main__":
    for i in range(1, 26):
        main(i)