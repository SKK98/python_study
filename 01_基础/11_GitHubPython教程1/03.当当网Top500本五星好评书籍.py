import json
import re

import requests

# https://vip.fxxkpython.com/?p=1903
# 主方法
def main(page):                                                                         # 这个是页数
    url = 'http://bang.dangdang.com/books/fivestars/01.00.00.00.00.00-recent30-0-0-1-' + str(page)
    html = request_dandan(url)
    items = parse_result(html) # 解析过滤我们想要的信息

    for item in items:
        write_item_to_file(item)


# 请求网页
def request_dandan(url):
   try:
       response = requests.get(url)
       if response.status_code == 200:
           return response.text
   except requests.RequestException:
       return None




# 解析网页
def parse_result(html):
    pattern = re.compile(
        '<li.*?list_num.*?(\d+)\.</div>.*?<img src="(.*?)".*?class="name".*?title="(.*?)">.*?class="star">.*?class="tuijian">(.*?)</span>.*?class="publisher_info">.*?target="_blank">(.*?)</a>.*?class="biaosheng">.*?<span>(.*?)</span></div>.*?<p><span class="price_n">(.*?)</span>.*?</li>', re.S)
    items = re.findall(pattern, html)

    for item in items:
        yield {
            'range': item[0],
            'image': item[1],
            'title': item[2],
            'recommend': item[3],
            'author': item[4],
            'times': item[5],
            'price': item[6]
        }


# 将信息写入文件
def write_item_to_file(item):
   print('开始写入数据 ====> ' + str(item))
   # 保存到当前目录的book.txt文件中
   with open('book.txt', 'a', encoding='UTF-8') as f:
       f.write(json.dumps(item, ensure_ascii=False) + 'n')
       f.close()


# 主函数
if __name__ == "__main__":
    for i in range(1, 26):
        main(i)