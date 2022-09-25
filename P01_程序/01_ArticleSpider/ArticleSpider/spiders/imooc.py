# -*- coding: utf-8 -*-
import scrapy


# scrapy crawl imooc

# 实在没办法了，可以用这种方法模拟登录，麻烦一点，成功率100%
class ImoocSpider(scrapy.Spider):
    name = 'imooc'
    allowed_domains = ['imooc.com']
    start_urls = ['https://www.imooc.com/']

    #想偷懒直接这样写不行
    # cookies={"Cookie":"*****"}

    #这样写才可以
    cookies={
        "zg_did":"%7B6980ed700d12e%22%7D",
        "UM_distinctid":"1701587b-7711b3e-144000-17015931db84bf",
        "Hm_lvt_f0cfcccd7b1393990c78efdeebff3968":",1582976265,1583336006",
        "redrainTime":"2020-3-4; IMCDNS=0",
        "imooc_uuid":"9f3b12bb-5a90-",
        "imooc_isnew":"1",
        "imooc_isnew_ct":"158423",
        "last_login_username":"834",
        "Hm_lpvt_f0cfcccd7b1393990c78efdeebff3968":"150",
        "cvde":"5e402b1",
        "loginstate":"1",
        "apsid":"M",
        "zg_f375fe2f71e542a4b890d9a620f9fb32":"%7B"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.FormRequest(url,cookies=self.cookies,callback=self.parse_page)

    def parse_page(self,response):
        print('========='+response.url)
        with open('deng.html','wb') as f:
            f.write(response.body)