# -*- coding: utf-8 -*-
__author__ = 'bobby'

from scrapy.cmdline import execute

import sys
import os

if __name__ == '__main__':
    """
        为什么使用__file__，而不使用sys.path.append("E:/Crawler_Project/ArticleSpider")
        原因：如果当前项目不在该路径下面或者部署到服务器上面，则会找不到该路径报错

        1.__file__ 当前文件路径——E:/Crawler_Project/ArticleSpider/main.py
        2.os.path.dirname(__file__)——E:/Crawler_Project/ArticleSpider
        3.os.path.abspath(__file__)——E:/Crawler_Project/ArticleSpider/main.py(原因:可能有些版本python使用file会输出main.py) 
    """
    # 获取当前文件目录
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # sys.path.append()将一个目录放至python搜索目录中
    # os.path.dirname()获取文件路径的文件夹路径——E:/Crawler_Project/ArticleSpider


    execute(["scrapy", "crawl", "jobbole"])
    # execute(["scrapy", "crawl", "zhihu"])
    # execute(["scrapy", "crawl", "lagou"])