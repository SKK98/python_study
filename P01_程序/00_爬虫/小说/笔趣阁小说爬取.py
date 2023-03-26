import requests
import time
from tqdm import tqdm
from bs4 import BeautifulSoup



def get_content(target):
    req = requests.get(url=target)
    req.encoding = 'utf-8'
    html = req.text
    bf = BeautifulSoup(html, 'lxml')
    texts = bf.find('article', id='article')        # 获取article
    content = texts.text.strip().split('\xa0' * 4)  # .text:获取文本内容 strip():去除空格 split():分割 \xa0:空格
    return content


if __name__ == '__main__':
    server = 'http://www.xsbiquge.org'
    book_name = 'test.txt'
    target = 'http://www.xsbiquge.org/book/1710/'
    req = requests.get(url=target, verify=False)    # verify=False 用于忽略证书验证
    req.encoding = 'utf-8'                          # 用于解决乱码问题
    html = req.text                                 # 获取网页源码
    chapter_bs = BeautifulSoup(html, 'lxml')        # 解析网页源码 第二个参数为解析器 lxml为解析器
    # 获取章节列表 获取class  =  "container border3-2 mt8 mb20"  下面的第二个div
    chapters = chapter_bs.find('div', class_='container border3-2 mt8 mb20').find_all('div')[1]

    chapters = chapters.find_all('a')               # 获取章节列表中的每一章
    for chapter in tqdm(chapters):                  # 进度条
        chapter_name = chapter.string               # 获取章节名称
        url = server + chapter.get('href')          # 获取章节链接
        content = get_content(url)
        with open(book_name, 'a', encoding='utf-8') as f:  # 写入文件 a:追加模式 encoding:编码 utf-8
            f.write(chapter_name)                           # 写入章节名称
            f.write('\n')                                   # 换行
            f.write('\n'.join(content))                     # 写入章节内容
            f.write('\n')                                   # 换行
