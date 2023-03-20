import requests
from bs4 import BeautifulSoup   # 网页解析，获取数据
import xlwt                     # 进行excel操作
import multiprocessing          # 多线程
import time
import sys

# 请求网页
def request_douban(url):
    # 伪装浏览器
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        if response.status_code == 200:     # 200表示请求成功
            return response.text
    except requests.RequestException:
        return None

# 解析网页
def main(url):
    sys.setrecursionlimit(1000000)    # 设置递归深度
    data = []
    html = request_douban(url)
    # soup = BeautifulSoup(html, 'lxml')
    soup = BeautifulSoup(html, 'html.parser')       # 解析器参数1：html.parser (python自带) 2：lxml (作用：解析速度快，文档容错能力强)
    list = soup.find(class_='grid_view').find_all('li')  # 找到所有电影
    for item in list:                                   # 遍历每个电影
        item_name = item.find(class_='title').string
        item_img = item.find('a').find('img').get('src')
        item_index = item.find(class_='').string
        item_score = item.find(class_='rating_num').string
        item_author = item.find('p').text
        item_intr = ''
        if (item.find(class_='inq') != None):
            item_intr = item.find(class_='inq').string
        print('爬取电影：' + item_index + ' | ' + item_name + ' | ' + item_score + ' | ' + item_intr)
        item = {
            'item_index': item_index,
            'item_name': item_name,
            'item_score': item_score,
            'item_intr': item_intr,
            'item_img': item_img,
            'item_author': item_author
        }
        data.append(item)
    return data


if __name__ == '__main__':
    startTime = time.time()
    data = []
    urls = []
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)        # 创建进程池 使用cpu核心数-1
    # 循环10次，每次25个电影
    for i in range(0, 10):
        url = 'https://movie.douban.com/top250?start=' + str(i * 25) + '&filter='
        urls.append(url)
    pool.map(main, urls)                        # 使用进程池, map()函数接收两个参数，一个是函数，一个是Iterable
    for pageItem in pool.map(main, urls):
        data.extend(pageItem)                   # extend()函数用于在列表末尾一次性追加另一个序列中的多个值
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('豆瓣电影Top250-test', cell_overwrite_ok=True)
    sheet.write(0, 0, '名称')
    sheet.write(0, 1, '图片')
    sheet.write(0, 2, '排名')
    sheet.write(0, 3, '评分')
    sheet.write(0, 4, '作者')
    sheet.write(0, 5, '简介')
    for index, item in enumerate(data):
        sheet.write(index + 1, 0, item['item_name'])
        sheet.write(index + 1, 1, item['item_img'])
        sheet.write(index + 1, 2, item['item_index'])
        sheet.write(index + 1, 3, item['item_score'])
        sheet.write(index + 1, 4, item['item_author'])
        sheet.write(index + 1, 5, item['item_intr'])
    book.save(u'豆瓣最受欢迎的250部电影-mul.xlsx')

    endTime = time.time()
    dtime = endTime - startTime
    print("程序运行时间：%s s" % dtime)  # 4.036666631698608 s