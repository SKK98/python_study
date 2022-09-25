# -*- coding: utf-8 -*-
import scrapy
import codecs

# 如果希望程序执行一开始就发送POST请求，可以重写Spider类的 start_requests(self)方法，并且不再调用start_urls里的url。
# 只要是需要提供post数据的，就可以用这种方法
# 下面示例：post数据是账户密码
class Imooc1Spider(scrapy.Spider):
    name = 'imooc1'
    allowed_domains = ['cnblogs.com']
    # start_urls = ['http://imooc.com/']

    def start_requests(self):
        url="https://account.cnblogs.com/signin?returnUrl=https:%2F%2Fnews.cnblogs.com%2F"
        yield scrapy.FormRequest(
            url=url,
            formdata={"username":"1310725169@qq.com","password":"45685279130LY*","referer":"https://account.cnblogs.com/signin?returnUrl=https:%2F%2Fnews.cnblogs.com%2F"}, #这里referer必须写上，不然会报错
            callback=self.parse_page
        )

    def parse_page(self,response):
        print('=========' + response.url)
        with codecs.open('deng1.json','wb',encoding = "utf-8") as f:
            f.write(response.body.decode('unicode_escape'))  #和codecs模块结合使用，将结果\u6210\u529f这种格式转换成中文