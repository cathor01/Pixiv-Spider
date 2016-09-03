# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sqlite3
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

from pixiv_hot.items import PixivItem, BigImage

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)


class PixivImagePipeline(ImagesPipeline):

    _cookie_key = 'pixiv_cookies'

    def file_path(self, request, response=None, info=None):
        if 'image_name' in request.meta:
            image_guid = request.url.split('.')[-1]
            if 'big' in request.meta:
                return 'origin/%s.%s' % (request.meta['image_name'], image_guid)
            return 'thumbs/%s.%s' % (request.meta['image_name'], image_guid)
        else:
            image_guid = request.url.split('/')[-1]
            return 'thumbs/%s' % image_guid

    def get_media_requests(self, item, info):
        if 'keyword' in item.fields:
            return [Request(x, meta={'cookiejar': self._cookie_key, 'image_name': item['id']}, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
                "Cache-Control": "max-age=0",
                "Referer": item['refer']
            })
                    for x in item.get(self.images_urls_field, [])]
        elif 'id' in item.fields:
            # print '12345555555555555555555555555'
            return [Request(x, meta={'cookiejar': self._cookie_key, 'big': '1',
                                     'image_name': u'{3}/{0}-{1}_{2}'.format(item['star'], item['id'].encode('gbk'), item['page'], item['img_save_dir'])},
                            headers={
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                                "Accept-Encoding": "gzip, deflate, sdch",
                                "Accept-Language": "zh-CN,zh;q=0.8",
                                "Connection": "keep-alive",
                                "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
                                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
                                "Cache-Control": "max-age=0",
                                "Referer": item['refer']
                            })
                    for x in item.get(self.images_urls_field, [])]


class PixivItemPipeline(object):
    conn = None

    def __init__(self):
        self.conn = self.create_table()
        # print '6666666666666666'

    def process_item(self, item, spider):
        if 'keyword' in item.fields:
            sql = u'insert into pixiv_item values(?, ?, ?, ?, ?, ?, ?)'
            self.conn.execute(sql, (
            item['id'], item['title'].encode('utf-8'), item['link'], item['star'], 1 if item['multi'] else 0,
            item['keyword'].encode('utf-8'), item['time'].strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
        return item

    def spider_closed(self, spider):
        self.conn.close()

    def create_table(self):
        conn = sqlite3.connect(get_project_settings()['DATABASE_POSITION'])
        conn.text_factory = str
        try:
            conn.execute(
                """CREATE TABLE pixiv_item(
                       id INTEGER PRIMARY KEY,
                       title TEXT, link TEXT,
                       star INTEGER, multi INTEGER,
                       keyword TEXT, publish TIMESTAMP)""")
            conn.commit()
        except:
            pass
        return conn
