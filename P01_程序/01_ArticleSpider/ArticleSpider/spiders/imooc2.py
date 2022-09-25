# -*- coding: utf-8 -*-
import scrapy

# 正统模拟登录方法：
# 首先发送登录页面的get请求，获取到页面里的登录必须的参数，比如说zhihu的 _xsrf
# 然后和账户密码一起post到服务器，登录成功
class Imooc2Spider(scrapy.Spider):
    name = 'imooc2'
    allowed_domains = ['imooc.com']
    start_urls = ['https://www.imooc.com/user/newlogin']

    def parse(self, response):
        # _xsrf = response.xpath("//_xsrf").extract()[0]
        yield scrapy.FormRequest.from_response(
            response,
            # formdata={"username": "", "password": "", "referer": "https://www.imooc.com","_xsrf" = _xsrf},
            formdata={"email": "", "password": "", "referer": "https://www.imooc.com"},  # 这里referer必须写上，不然会报错
            callback=self.page_parse    # #登录成功后,调用page_parse回调函数
        )

    def page_parse(self,response):
        print('====1=====' + response.url)
        url="https://www.imooc.com/"
        yield scrapy.Request(url,callback=self.new_page)

    def new_page(self,response):
        print('====2====='+response.url)
        with open('deng2.html','wb') as f:
            f.write(response.body)

'''
报错了：ValueError: No <form> element found in <200 https://www.imooc.com/user/newlogin>
查了下原因，见：https://stackoverflow.com/questions/22707184/scrapy-request-form-for-scraping-data
中文翻译如下：
您提到的页面不是有效的HTML。看起来这是一个SSI块，应该是另一页的一部分。
您之所以会出错，是因为此页面大量使用Javascript。它没有form request。from_response尝试使用现有表单发出请求，但表单不存在。
您应该处理整个页面，或者手动填充表单请求的属性，然后将其从整个页面提交到URL。
'''