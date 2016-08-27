# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PixivItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    id = scrapy.Field()
    star = scrapy.Field()
    link = scrapy.Field()
    multi = scrapy.Field()
    keyword = scrapy.Field()
    time = scrapy.Field()
    refer = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()


class BigImage(scrapy.Item):
    id = scrapy.Field()
    star = scrapy.Field()
    refer = scrapy.Field()
    page = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
