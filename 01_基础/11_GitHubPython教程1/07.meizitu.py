# encoding = utf-8
import concurrent                                   # 用于线程池
import os                                           # 用于创建文件夹
from concurrent.futures import ThreadPoolExecutor   # 用于线程池
import requests                                     # 用于请求网页
from bs4 import BeautifulSoup                       # 用于解析网页

# 构造请求头
def header(referer):

    headers = {
        'Host': 'i.meizitu.net',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': '{}'.format(referer),
    }

    return headers

# 请求网页
def request_page(url):
    try:
        response = requests.get(url)            # 请求网页
        if response.status_code == 200:         # 判断请求是否成功
            return response.text                # 返回网页内容
    except requests.RequestException:           # 请求失败
        return None                             # 返回空

# 获取每一页的链接和名称
def get_page_urls():
    # 获取每一页的链接
    for i in range(1, 2):
        baseurl = 'https://www.mzitu.com/page/{}'.format(i)
        html = request_page(baseurl)
        soup = BeautifulSoup(html, 'lxml')
        elements = soup.find(class_='postlist').find_all('li')
        urls = []
        for item in elements:
            url = item.find('span').find('a').get('href')
            print('页面链接：%s' % url)
            urls.append(url)

    return urls

# 下载图片
def download_Pic(title, image_list):
    # 新建文件夹
    os.mkdir(title)
    j = 1
    # 下载图片
    for item in image_list:
        filename = '%s/%s.jpg' % (title, str(j))
        print('downloading....%s : NO.%s' % (title, str(j)))
        with open(filename, 'wb') as f:
            img = requests.get(item, headers=header(item)).content
            f.write(img)
        j += 1
# 获取每一个详情妹纸
def download(url):
    html = request_page(url)
    soup = BeautifulSoup(html, 'lxml')
    total = soup.find(class_='pagenavi').find_all('a')[-2].find('span').string
    title = soup.find('h2').string
    image_list = []

    for i in range(int(total)):
        html = request_page(url + '/%s' % (i + 1))
        soup = BeautifulSoup(html, 'lxml')
        img_url = soup.find('img').get('src')
        image_list.append(img_url)

    download_Pic(title, image_list)

# 多线程下载
def download_all_images(list_page_urls):
    # 获取每一个详情妹纸
    # works = len(list_page_urls)
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as exector:
        for url in list_page_urls:
            exector.submit(download, url)

# 主函数
if __name__ == '__main__':
    # 获取每一页的链接和名称
    list_page_urls = get_page_urls()        # 获取每一页的链接和名称
    download_all_images(list_page_urls)     # 多线程下载