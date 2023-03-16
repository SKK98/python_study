import requests

# get请求
rget = requests.get('https://api.github.com/events')

# post请求
rpost = requests.post('https://httpbin.org/post', data={'key': 'value'})

# 其它乱七八糟的 Http 请求
#  r = requests.put('https://httpbin.org/put', data = {'key':'value'})
# r = requests.delete('https://httpbin.org/delete')
# r = requests.head('https://httpbin.org/get')
# r = requests.options('https://httpbin.org/get')

# 传递 URL 参数
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.get('https://httpbin.org/get', params=payload)


# 假装自己是浏览器
url = 'https://api.github.com/some/endpoint'
headers = {'user-agent': 'my-app/0.0.1'}
r = requests.get(url, headers=headers)

# 获取服务器响应文本内容
r = requests.get('https://api.github.com/events')
r.text          # 字符串形式的响应体，会自动根据响应头部的字符编码进行解码。
r.encoding      # 从 HTTP header 中猜测的响应内容编码方式。
r.content       # 以字节形式（二进制）返回。

r = requests.get('https://httpbin.org/get')
r.status_code   # 响应状态码
r.headers       # 获取响应头 以字典对象存储服务器响应头，但是这个字典比较特殊，字典键不区分大小写，也就是说，可以用 r.headers['content-type'] 或者 r.headers['Content-Type'] 都可以访问到内容类型。
# {
#     'content-encoding': 'gzip',
#     'transfer-encoding': 'chunked',
#     'connection': 'close',
#     'server': 'nginx/1.0.4',
#     'x-runtime': '148ms',
#     'etag': '"e1ca502697e5c9317743dc078f67693f"',
#     'content-type': 'application/json'
#
# }

r = requests.get('https://api.github.com/events')
r.json()    # Requests 中内置的 JSON 解码器，以 json 格式返回，前提返回的内容确实是 json 格式的，否则就会抛出异常。


r = requests.get('https://api.github.com/events', stream=True)
r.raw     # 获取 socket 流响应内容  返回原始响应体，也就是 urllib 的 response 对象，使用 r.raw.read() 读取。

r.raw.read(10)  # 读取前10个字节


# Post请求
payload_tuples = [('key1', 'value1'), ('key1', 'value2')]
r1 = requests.post('https://httpbin.org/post', data=payload_tuples)
payload_dict = {'key1': ['value1', 'value2']}
r2 = requests.post('https://httpbin.org/post', data=payload_dict)
print(r1.text)
r1.text == r2.text # True

#请求的时候用 json 作为参数
url = 'https://api.github.com/some/endpoint'
payload = {'some': 'data'}
r = requests.post(url, json=payload)

# 想上传文件？
url = 'https://httpbin.org/post'
files = {'file': open('report.xls', 'rb')}
r = requests.post(url, files=files)
r.text
# {  ...  "files": {    "file": "<censored...binary...data>"  },  ...}


# 获取 cookie 信息
url = 'http://example.com/some/cookie/setting/url'
r = requests.get(url)
r.cookies['example_cookie_name']
# 'example_cookie_value'


# 发送 cookie 信息
url = 'https://httpbin.org/cookies'
cookies = dict(cookies_are='working')
r = requests.get(url, cookies=cookies)
r.text
# '{"cookies": {"cookies_are": "working"}}'


# 设置超时
requests.get('https://github.com', timeout=0.001)












