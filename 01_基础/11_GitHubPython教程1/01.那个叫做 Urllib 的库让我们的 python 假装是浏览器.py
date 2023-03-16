import urllib.request
from urllib import request, parse
import ssl

# 打印网页源码
# 参数1: url 参数2: data 参数3: timeout
# response = urllib.request.urlopen('http://www.baidu.com')
# print(response.read().decode('utf-8'))



# 如果我们要欺骗服务器说我们是浏览器或者手机请求的呢？ 这个时候我们需要添加请求头信息

context = ssl._create_unverified_context()

#  接着定义一下我们的请求 url 和 headers
url = 'https://biihu.cc//account/ajax/login_process/'
headers = {
    # 假装自己是浏览器
    'User-Agent': ' Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}
#  再定义一下我们的请求参数
dict = {
    'return_url': 'https://biihu.cc/',
    'user_name': 'xiaoshuaib@gmail.com',
    'password': '123456789',
    '_post_type': 'ajax',
}

data = bytes(parse.urlencode(dict), 'utf-8')
req = request.Request(url,data=data,headers=headers,method='POST')

response = request.urlopen(req,context=context)
print(response.read().decode('utf-8'))