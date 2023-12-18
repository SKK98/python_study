import requests
import re
import pandas as pd
from fake_useragent import UserAgent
import threading

# 定义百度贴吧的url
# url = 'https://tieba.baidu.com/f?kw=V&ie=utf-8&pn='                    # V吧
url = 'https://tieba.baidu.com/f?kw=%CB%EF%D0%A6%B4%A8&ie=utf-8&pn='     # 孙笑川吧
# 生成随机的User-Agent
ua = UserAgent()
# 定义请求头
headers = {
    'User-Agent': ua.random}

# 定义空列表，用于存储爬取到的数据
titles = []
links = []
linkKey_set = set()
replyNums = []

# 自动计算每页多少条 根据t_con cleafix有多少个
t_con = 50
cleafix = 100
page_num = cleafix // t_con
if cleafix % t_con != 0:
    page_num += 1

def get_data(i):
    full_url = url + str(i)
    # 发送请求
    r = requests.get(full_url, headers=headers)
    # 使用正则表达式提取数据
    for title, link, linkKey, replyNum in zip(re.findall('<a rel="noopener" href=".*?" title="(.*?)" target="_blank" class="j_th_tit ">', r.text),
                                             ['https://tieba.baidu.com' + link for link in re.findall('<a rel="noopener" href="(.*?)" title=".*?" target="_blank" class="j_th_tit ">', r.text)],
                                             re.findall('<a rel="noopener" href="(.*?)" title=".*?" target="_blank" class="j_th_tit ">', r.text),
                                             [int(num) for num in re.findall('<span class="threadlist_rep_num center_text".*?>(.*?)</span>', r.text, re.S)]):
        # 判断是否已经爬取过该链接
        if linkKey not in linkKey_set:
            titles.append(title)
            links.append(link)
            linkKey_set.add(linkKey)
            replyNums.append(replyNum)

threads = []
# 循环爬取100页的数据，每页50条
for i in range(0, page_num * t_con, t_con):
    t = threading.Thread(target=get_data, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# 将数据存储到DataFrame中，并按回复数降序排列
df = pd.DataFrame({'Title': titles, 'Link': links, 'LinkKey': list(linkKey_set), 'ReplyNum': replyNums})
df = df.sort_values(by='ReplyNum', ascending=False)
# 将数据保存到Excel文件中
df.to_excel('tieba_python.xlsx', index=False)
