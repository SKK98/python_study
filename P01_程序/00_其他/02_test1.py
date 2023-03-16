import urllib.request


# 返回网页源码
response = urllib.request.urlopen('http://www.baidu.com')
print(response.read().decode('utf-8'))