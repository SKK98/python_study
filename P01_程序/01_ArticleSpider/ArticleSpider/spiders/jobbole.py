# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse
import json
import requests
from scrapy.loader import ItemLoader

from utils.common import get_md5
from items import JobBoleArticleItem, ArticleItemLoader


from pydispatch import dispatcher
from scrapy import signals


# 流程：获取网页 -> 获取css节点 -> 找到文章url -> 找到文章内容
class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']
    custom_settings = {
        "COOKIES_ENABLED": True
    }


    """ 
            手动登录拿到cookie并放入到scrapy,降低难度
            1.第一个案例是最简单的案例，需要登录才能访问
            2.第二个案例 知乎：花费大量的时间讲解模拟登录
            3.拉勾网 — crawlspider ：拉勾反爬越来越严重，crawlspider用途不大
        """

    # spider运行起来，URL都会从此方法开始
    def start_requests(self):

        # 入口可以模拟登录拿到cookie，selenium控制浏览器会被一些网站识别出来(例如:知乎、拉勾网)

        # 实例化一个浏览器
        import undetected_chromedriver.v2 as uc
        chrome_driver = r"E:\Python1\chromedriver.exe"
        # 后面讲解selenium的时候会下载chromedriver.exe
        browser = uc.Chrome(executable_path=chrome_driver)
        browser.get("https://account.cnblogs.com/signin")

        input("回车继续：")  # 等待浏览器驱动加载完成  # 自动化输入、自动化识别滑动验证码并拖动整个自动化过程

        # 手动登录后获取cookie值
        cookies = browser.get_cookies()
        cookie_dict = {}  # 将获取的cookie值转变为dict字典类型数据
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        # 爬虫的时候不要过快，建议使用debug模式进行运行，否则网站会监测cookie值，然后禁止该cookie

        for url in self.start_urls:
            # 将cookie交给scrapy，那么后序的请求会沿用之前请求的cookie值吗？
            headers = {
                # headers将访问伪装成浏览器，防止被反爬
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/101.0.4951.64 Mobile Safari/537.36'
            }
            '''
                dont_filter参数解析(url去重)
                1.dont_filter是根据request来去重的，但是这里的request不是简单的url去重那么简单，而是scrapy有一套指纹的生成方法.
                2.例如同一个url但是是post的请求，post参数不一样也不能认为是同一个请求，后面的scrapy-redis源码分析中会讲解到这个的，
                  如果你是get请求，那么你就简单的理解为通过url去重，这样的好处是这个数据爬取过你就不用再爬取了，不然重复爬取耗费性能啊，
                3.但是说到这里我得提出另一个需求：
                        如果你的url相同的页面，可能数据每次访问都不一样，那么是不是该重复爬取呢？ - 比如列表页
                        如果你的url相同的页面，虽然数据都一样，但是有可能用户会更新里面的内容呢？ -比如文章详情页
                4.所以我们不能说： 这个页面没有必要重复抓取， 但是另一方面大量的情况确实： 大部分的详情页个不会更新或者更新概率极低，
                    这个时候没有必要去抓取最新的数据，毕竟过滤抓取过的页面，这样效率高啊
                所以：具体请求具体分析，scrapy提供了这个参数就是让你自己去决定这个数据是应该过滤掉还是可以重复抓取
            '''
            yield scrapy.Request(url, cookies=cookie_dict, headers=headers, dont_filter=True)

    # 能够进入parse()函数，则表示从http://news.cnblogs.com/下载已经完成
    def parse(self, response, **kwargs):
        """
            parse()方法作用：
            1.获取新闻列表页中的新闻url并交给scrapy进行下载后调用相应的解析方法parse_detail()、parse_num()
            2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse()继续跟进

            例如：第一页第一个新闻标题xpath路径(@取属性)
                根据级一级一级往下查询，但是如果页面变化则会找不到
                  response.xpath("/html/body/div[2]/div[2]/div[4]/div[1]/div[2]/h2/a/@href")
                根据id获取，id唯一
                  //*[@id="entry_721263"]/div[2]/h2/a/@href
        """
        '''
            url = response.xpath('//*[@id="entry_721263"]/div[2]/h2/a/@href').extract_first("")
            extract_first("")提取SelectList中的第一个值，没有则返回""空值

            url = response.xpath('//div[@id="news_list"]/div[1]/div[2]/h2/a/@href').extract_first("")
            url = response.xpath('//div[@id="news_list"]//h2[@class="news_entry"]/a/@href').extract()
        '''
        # 获取详情页的URL地址集
        post_nodes = response.xpath("//div[@id='news_list']/div")
        # post_nodes = response.css('#news_list .news_block')[1:2]
        for post_node in post_nodes:
            '''
                post_node.xpath开始以后就要是相对路径——.//h2[@class='news_entry']/a/@href
                1.如果写成xpath('//*')  //开头的就会从整个url开头找起
                2.必须写成.//
            '''

            post_url = post_node.xpath(".//h2[@class='news_entry']/a/@href").extract_first("")  # 获取详情页URL地址(子路径"/n/721304/")
            # 返回至python则为/n/721304/，而浏览器中会自动将当前域名增加https://news.cnblogs.com/n/721304/
            image_url = post_node.xpath(".//div[@class='entry_summary']/a/img/@src").extract_first("")  # 图片地址
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            # image_url = post_node.css(".entry_summary a img::attr(src)").extract_first("")

            """
                1.urljoin()方法将两个链接参数拼接为完整URL,用于拼接url(无论post_url是完整还是非完整的url地址)
                    如果post_url是一个完整的url地址(即https://news.cnblogs.com/n/721304/)，则不会将response.url拼接到前面
                    如果post_url不是一个完整的url地址(即/n/721304/)，则会自动将https://news.cnblogs.com拼接到前面

                2.callback表示Request()请求结束后，交给parse_detail()方法进行处理
                    注:一定不能写parse_detail(),写parse_detail()会运行该方法,但是此处需求是当Request下载完成后,调用该方法
                       parse_detail()则会有返回值，返回给callback=**

                3.yield Request()后为什么没有跳转至parse_detail()方法而是继续for循环，为什么不是yield后立刻跳转至
                    parse_detail()方法？
                    原因：1.Scrapy是一个异步的框架，异步框架意味着当遇到一个url地址交出去之后，交出去之后会继续执行
                          2.服务器没有那么快返回，交出Request后服务器没有那么快返回数据，这时候就可以继续进行for循环，将
                             其中的数据逐步交出去
                    注：比较好的debug方式:不在下面的yield Request()打断点，而是在def parse_detail()方法中打断点
            """
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
        # next_url = response.css("div.pager a:last-child::text").extract_first("")

        # 判断是否有下一页 如果有则parse()方法继续执行
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)


    # 新闻详情页面数据抓取
    def parse_detail(self, response):
        # 正则匹配 .*?(\d+).* 匹配url中的数字
        match_re = re.match(".*?(\d+).*", response.url)
        # 判断response.url地址是否包含新闻详情的id
        if match_re:
            # 新闻详情的id
            post_id = match_re.group(1)

            """
            article_item = JobBoleArticleItem()  # 创建Item对象

            # 获取新闻详情标题
            title = response.xpath("//*[@id='news_title']//a/text()").extract_first("")
            # title = response.css("#news_title a::text").extract_first("")

            # 新闻详情发布时间
            create_date = response.xpath("//*[@id='news_info']//*[@class='time']/text()").extract_first("")
            # create_date = response.css("#news_info .time::text").extract_first("")
            re_match = re.search(".*?(\d+.*)", create_date)
            if re_match:
                create_date = re_match.group(1)

            # 新闻详情内容
            content = response.xpath("//*[@id='news_content']").extract()[0]
            # content = response.css("#news_content").extract()[0]

            # 新闻详情标签
            tag_list = response.xpath("//*[@class='news_tags']/a/text()").extract()
            # tag_list = response.css(".news_tags a::text").extract()
            tags = ",".join(tag_list)  # 原因：可能某些文章并没有tag标签

            # 新闻详情HTML页面直接提取点赞数、评论数、查看数(注:直接获取html代码则为None，该数据由js返回)
            '''
                1.浏览器中看到的html页面是浏览器执行过js程序后所呈现的页面
                2.js逻辑非常强大，服务器中可能不存在该元素但是js可能写入该元素
                注：通过Scrapy下载的页面实际上是服务器返回的原始的html，并不是浏览器中看到的html
                # comment_num = response.xpath("//a[@id='News_CommentCount_Head']/text()").extract_first("")
                # comment = response.css("#news_info span.comment a::text").extract()
            '''

            article_item['title'] = title
            article_item['create_date'] = create_date
            article_item['url'] = response.url
            # 获取parse()方法yield的Request的meta中的值  注：article_item['front_image_url']数据类型必须为list类型
            if response.meta.get("front_image_url", []):
                article_item["front_image_url"] = [response.meta.get("front_image_url", "")]
            else:
                article_item["front_image_url"] = []
            article_item['tags'] = tags
            article_item['content'] = content
            """

            item_loader = ItemLoader(item=JobBoleArticleItem(), response=response)
            item_loader.add_xpath("title", "//*[@id='news_title']//a/text()")
            item_loader.add_xpath("content", "//*[@id='news_content']")
            item_loader.add_xpath("tags", "//*[@class='news_tags']/a/text()")
            item_loader.add_xpath("create_date", "//*[@id='news_info']//*[@class='time']/text()")
            item_loader.add_value("url", response.url)
            item_loader.add_value("front_image_url", response.meta.get("front_image_url", ""))

            article_item = item_loader.load_item()

            '''
                yield Request(url=parse.urljoin(response.url, "NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
                URL地址拼接问题？
                    上述方式拼接的url结果：https://news.cnblogs.com/n/724466/NewsAjax/GetAjaxNewsInfo?contentId=724466
                    而正确的url地址：https://news.cnblogs.com/NewsAjax/GetAjaxNewsInfo?contentId=724466
                    原因：如果写NewsAjax/GetAjaxNewsInfo?contentId=724466则将其作为https://news.cnblogs.com/n/724466子路径
                          如果写/NewsAjax/GetAjaxNewsInfo?contentId=724466则将其加入至https://news.cnblogs.com子域名下
            '''
            yield article_item

            # yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
            #               meta={'article_item': article_item}, callback=self.parse_num)

    # 获取新闻详情点赞数、评论数、查看数（初始不存在于原始html中）
    def parse_num(self, response):
        """
            response.text——'{"ContentID":724466,"CommentCount":0,"TotalView":31,"DiggCount":0,"BuryCount":0}'
            response.text的数据类型type: str
            json.loads(response.text)——将str类型数据转化为dict字典类型
        """
        j_data = json.loads(response.text)

        """
            meta是一个字典，它的主要作用是用来传递数据的
            1.meta = {‘key1’:value1}，如果想在下一个函数中取出value1, 只需得到上一个函数的meta[‘key1’]即可
            2.因为meta是随着Request产生时传递的，下一个函数得到的Response对象中就会有meta，即response.meta
        """
        article_item = response.meta.get('article_item', "")  # 获取parse_detail()中yield的Request()传递的meta

        praise_num = j_data['DiggCount']  # 点赞数
        comment_num = j_data['CommentCount']  # 评论数
        view_num = j_data['TotalView']  # 查看数

        article_item['praise_nums'] = praise_num
        article_item['view_nums'] = view_num
        article_item['comment_nums'] = comment_num

        # 如何生成url的url_object_id(不定长字符串生成MD5)
        article_item['url_object_id'] = get_md5(article_item['url'])

        yield article_item


    # #收集伯乐在线所有404的url以及404页面数
    # handle_httpstatus_list = [404]
    #
    # def __init__(self, **kwargs):
    #     self.fail_urls = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self, spider, reason):
    #     self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))
    #
    #
    #
    # # 解析 列表页中的  所有文章url  并交给scrapy下载后 并进行 解析
    # def parse(self, response):
    #     """
    #     1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
    #     2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
    #     """
    #     # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
    #     if response.status == 404:
    #         self.fail_urls.append(response.url)
    #         self.crawler.stats.inc_value("failed_url")
    #
    #     # 获取css节点                                        [:1]
    #     post_nodes = response.css('#news_list .news_block')
    #     # 遍历css节点去除所有图片url
    #     for post_node in post_nodes:
    #         image_url = post_node.css('.entry_summary a img::attr(src)').extract_first("")
    #         if image_url.startswith("//"):
    #             image_url = "https:" + image_url
    #             # extract_first()   方法只能返回第一个值，如果没有值，则返回None
    #             # extract()         方法可以返回所有值，如果没有值，则返回一个空列表
    #         post_url = post_node.css('h2 a::attr(href)').extract_first("")
    #
    #         # yield 是用来提交给scrapy的，这里是提交给scrapy下载后并进行解析
    #         # urljoin() 方法用于拼接两个或多个字符串，返回一个新的字符串。
    #         yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
    #                       callback=self.parse_detail)
    #         break
    #
    #         # 提取下一页并交给scrapy进行下载 , 如果是下一页的就获取下一页的url(href中的)并交给scrapy进行下载
    #         # next_url = response.xpath("//a[contains(text(), 'Next >')]/@href").extract_first("")
    #         # if next_url:
    #         #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
    #
    # # 解析详情页面
    # def parse_detail(self, response):
    #     match_re = re.match(".*?(\d+.*)", response.url)  # 获取utl中的数字（就是这个网页访问的查询id）
    #     if match_re:
    #         item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
    #         item_loader.add_css("title", "#news_title a::text")
    #         item_loader.add_css("create_date", "#news_info .time::text")
    #         item_loader.add_css("content", "#news_content")
    #         item_loader.add_css("tags", ".news_tags a::text")
    #         item_loader.add_value("url", response.url)
    #         # 如果图片路径没有值，则返回空
    #         if response.meta.get("front_image_url", []):
    #             item_loader.add_value("front_image_url", response.meta.get("front_image_url", []))
    #
    #     yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
    #                   meta={"article_item": item_loader, "url": response.url}, callback=self.parse_nums)
    #
    # # 回调 接口 返回 获取评论数喜欢数等
    # def parse_nums(self, response):
    #     j_data = json.loads(response.text)
    #     item_loader = response.meta.get("article_item", "")
    #
    #     praise_nums = j_data["DiggCount"]
    #     fav_nums = j_data["TotalView"]
    #     comment_nums = j_data["CommentCount"]
    #
    #     item_loader.add_value("praise_nums", j_data["DiggCount"])
    #     item_loader.add_value("fav_nums", j_data["TotalView"])
    #     item_loader.add_value("comment_nums", j_data["CommentCount"])
    #     item_loader.add_value("url_object_id", get_md5(response.meta.get("url", "")))
    #     '''
    #     article_item["praise_nums"] = praise_nums
    #     article_item["fav_nums"] = fav_nums
    #     article_item["comment_nums"] = comment_nums
    #     article_item["url_object_id"] = common.get_md5(article_item["url"])
    #     '''
    #
    #     article_item = item_loader.load_item()
    #
    #     yield article_item



