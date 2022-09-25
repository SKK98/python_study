# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter

# 引入 实现图像缩略图生成逻辑的抽象管道
from scrapy.pipelines.images import ImagesPipeline
# 处理文件 & 编码
import codecs
import json
# 导出
from scrapy.exporters import JsonItemExporter

import MySQLdb
import MySQLdb.cursors

# 引入异步操作
from twisted.enterprise import adbapi


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


# 自定义json文件的导出
class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        # w: 写入模式 a: 追加模式
        self.file = codecs.open('article.json', 'w', encoding="utf-8")

    # 重写父类的方法
    def process_item(self, item, spider):
        # 将item转换为字典 再 转换为json字符串
        lines = json.dumps(dict(item), ensure_ascii=False, default=json_serial) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# Spider 内置的 Json导出
class JsonExporterPipleline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        # wb: 二进制写入模式
        self.file = open('articleexport.json', 'wb')
        #                                                             ensure_ascii=False: 不使用ascii编码 用于输出中文
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 图片 路径
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ""
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item


# 采用同步的机制写入mysql
class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.152.233', 'root', '123456', 'article_spider', charset="utf8",
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    # insert into jobbole_article(title, url, create_date, fav_nums)
    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article( title, url, url_object_id, front_image_path, front_image_url, parise_nums, comment_nums, fav_nums, tags, content, create_date)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            
        """
        front_image = ",".join(item.get("front_image_url", []))
        self.cursor.execute(insert_sql, (
            item["title", ""], item["url", ""], item["url_object_id", ""], item["front_image_path", ""],
            front_image, item["parise_nums", ""], item["comment_nums", ""], item["fav_nums", ""],
            item["tags", ""], item["content", ""], item["create_date", "1970-07-01"]))
        self.conn.commit()


# 异步mysql插入
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # from_settings: 从settings.py中读取配置
    @classmethod
    def from_settings(cls, settings):
        from MySQLdb.cursors import DictCursor
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            # cursorclass=DictCursor,
            use_unicode=True,
        )
        # python 中 * 代表将列表解包 ** 代表将字典解包  *** 代表将字典解包后再解包

        # 使用adbapi连接池  **dbparms: 将字典转换为关键字参数
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    # process_item: 会自动调用 参数: item: 参数
    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行 参数1: 调用的函数 参数2: 传递的参数
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常
        return item

    # handle_error: 处理异常
    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    # do_insert: 插入数据
    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
