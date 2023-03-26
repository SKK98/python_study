import requests
import os
import re
from bs4 import BeautifulSoup
from contextlib import closing
from tqdm import tqdm
import time

# 创建保存目录
save_dir = '妖神记'
if save_dir not in os.listdir('./'):  # 如果没有这个目录，就创建
    os.mkdir(save_dir)
# 目标网址
target_url = "https://www.dmzj.com/info/yaoshenji.html"

# 获取动漫章节链接和章节名
r = requests.get(url=target_url)                    # 获取网页
bs = BeautifulSoup(r.text, 'lxml')                  # 解析网页
list_con_li = bs.find('ul', class_="list_con_li")   # 获取章节列表
cartoon_list = list_con_li.find_all('a')            # 获取章节链接和章节名
chapter_names = []                                  # 章节名
chapter_urls = []                                   # 章节链接

# 获取章节名和章节链接
for cartoon in cartoon_list:
    href = cartoon.get('href')                  # 获取章节链接
    name = cartoon.text                         # 获取章节名
    chapter_names.insert(0, name)               # 将章节名插入到列表中
    chapter_urls.insert(0, href)                # 将章节链接插入到列表中

# 下载漫画      进度条
#  enumerate() 函数用于将一个可遍历的数据对象（如列表、元组或字符串）组合为一个索引序列，同时列出数据和数据下标
#  enumerate(sequence, [start=0]) sequence -- 一个序列、迭代器或其他支持迭代对象。start -- 下标起始位置。
#  enumerate() 函数返回 enumerate(枚举) 对象。该对象的 __next__() 方法返回一个元组，里面包含一个计数值（从 start 开始，默认为 0），和通过迭代 sequence 获得的下一个值。
#  tqdm() 函数用于在 Python 长循环中添加一个进度提示信息，用户只需要封装任意的迭代器 tqdm(iterator)。
for i, url in enumerate(tqdm(chapter_urls)):
    download_header = {
        'Referer': url      # Referer 指的是请求来源，即从哪个页面链接过来的
    }
    name = chapter_names[i]     # 获取章节名
    # 去掉.
    while '.' in name:
        name = name.replace('.', '')
    chapter_save_dir = os.path.join(save_dir, name)     # 章节保存目录, os.path.join() 函数用于路径拼接
    if name not in os.listdir(save_dir):                # 如果没有这个目录，就创建
        os.mkdir(chapter_save_dir)                          # 创建目录
    r = requests.get(url=url)                           # 获取网页
    html = BeautifulSoup(r.text, 'lxml')                # 解析网页
    script_info = html.script                           # 获取script标签
    pics = re.findall('\d{13,14}', str(script_info))    # 获取图片链接 \d{13,14} 的意思是匹配13到14个数字
    for j, pic in enumerate(pics):                      # 修正图片链接
        if len(pic) == 13:
            pics[j] = pic + '0'
    pics = sorted(pics, key=lambda x: int(x))           # 排序
    chapterpic_hou = re.findall('\|(\d{5})\|', str(script_info))[0]     # 获取图片链接后缀
    chapterpic_qian = re.findall('\|(\d{4})\|', str(script_info))[0]    # 获取图片链接前缀
    for idx, pic in enumerate(pics):
        if pic[-1] == '0':
            url = 'https://images.dmzj.com/img/chapterpic/' + chapterpic_qian + '/' + chapterpic_hou + '/' + pic[:-1] + '.jpg'
        else:
            url = 'https://images.dmzj.com/img/chapterpic/' + chapterpic_qian + '/' + chapterpic_hou + '/' + pic + '.jpg'
        pic_name = '%03d.jpg' % (idx + 1)
        pic_save_path = os.path.join(chapter_save_dir, pic_name)
        with closing(requests.get(url, headers=download_header, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                with open(pic_save_path, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
            else:
                print('链接异常')
    time.sleep(10)
