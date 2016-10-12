# -*- coding: utf-8 -*-

import json
import re

import datetime
import scrapy
import platform

from pixiv_hot.items import PixivItem, BigImage

from scrapy.utils.project import get_project_settings


class ImageCrawler(scrapy.Spider):
    name = "pixiv"

    max_page = 5

    current = 1

    url_list = []

    _cookie_key = 'pixiv_cookies'

    search_root = u'http://www.pixiv.net/search.php'

    url_root = u'http://www.pixiv.net'

    manga_root = u'http://www.pixiv.net/member_illust.php?mode=manga&illust_id='

    single_root = u'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='

    pixiv_id = ''

    pixiv_pass = ''

    keyword = ''

    save_star = 500

    time_pattern = r'img/(\d{4})/(\d{2})/(\d{2})/(\d{2})/(\d{2})/(\d{2})'

    save_thumbs = True

    img_save_dir = u'big'

    def __init__(self, keyword, oneof=u'', exclude=u'', max_page=0, save_star=500, save_thumbs=True, save_dir=u'big', *args, **kwargs):
        super(ImageCrawler, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        
        self.pixiv_id = settings['PIXIV_ID']
        self.pixiv_pass = settings['PIXIV_PASS']
        self.max_page = int(max_page)
        print keyword
        if platform.system() == 'Windows':
            self.keyword = keyword.decode('gbk').replace('##', ' ')
            if oneof is not None and oneof != u'':
                self.keyword += u' (' + oneof.decode('gbk').replace('##', ' OR ') + u')'
            if exclude is not None and exclude != u'':
                excludes = exclude.split('##')
                for excl in excludes:
                    self.keyword += u' -' + excl.decode('gbk')
            self.img_save_dir = save_dir.decode('gbk')
        else:
            self.keyword = keyword.replace('##', ' ')
            if oneof is not None and oneof != u'':
                self.keyword += u' (' + oneof.replace('##', ' OR ') + u')'
            if exclude is not None and exclude != u'':
                excludes = exclude.split('##')
                for excl in excludes:
                    self.keyword += u' -' + excl
            self.img_save_dir = save_dir
        self.save_star = int(save_star)
        self.save_thumbs = save_thumbs == 'True' or save_thumbs == True
        print self.keyword, self.max_page, self.save_star, self.save_thumbs

    def start_requests(self):
        request = scrapy.Request(
            'http://accounts.pixiv.net/login', callback=self.pre_login, method='GET',
            meta={'cookiejar': self._cookie_key}, dont_filter=True)
        return [request, ]

    def pre_login(self, response):
        pattern = r'postKey":"([a-zA-Z0-9]+)"'
        m = re.search(pattern, response.body)
        return scrapy.FormRequest(
            url='https://accounts.pixiv.net/login', callback=self.after_login,
            formdata={
                'pixiv_id': self.pixiv_id,
                'password': self.pixiv_pass,
                'post_key': m.group(1),
                'skip': '1',
                'mode': 'login'
            },
            meta={'cookiejar': response.meta['cookiejar']}, dont_filter=True)

    def after_login(self, response):
        if response.url.find('www.pixiv.net') > -1:
            return scrapy.Request(
                url=self.search_root + u'?word=' + self.keyword,
                meta={'cookiejar': response.meta['cookiejar']},
                dont_filter=True, callback=self.parse)
        result = json.loads(response.body)
        if not result['error']:
            return scrapy.Request(
                url=self.search_root + u'?word=' + self.keyword,
                meta={'cookiejar': response.meta['cookiejar']},
                dont_filter=True, callback=self.parse)
        else:
            print result['message']

    def parse(self, response):
        root = response.selector
        # print '2333333333333333333333'
        next = root.xpath('//span[@class="next"]/a/@href')
        if next is None or len(next) == 0:
            next_page = None
        else:
            next_page = self.search_root + next.extract_first()
        lis = root.xpath('//ul[@class="_image-items autopagerize_page_element"]/li[@class="image-item"]')
        # print lis
        for li in lis:
            item = PixivItem()
            a = li.xpath('./a[2]')
            item['title'] = a.xpath('./h1/text()').extract_first()
            item['link'] = self.url_root + a.xpath('@href').extract_first()
            image_a = li.xpath('./a[1]')
            temp = image_a.xpath('@class').extract_first()
            if temp.find('multi') > -1:
                item['multi'] = True
            else:
                item['multi'] = False
            img = image_a.xpath('./div/img/@src').extract_first()
            item['image_urls'] = [img, ]
            time_m = re.search(self.time_pattern, img)
            if time_m is not None:
                item['time'] = datetime.datetime(year=int(time_m.group(1)), month=int(time_m.group(2)),
                                                 day=int(time_m.group(3)), hour=int(time_m.group(4)),
                                                 minute=int(time_m.group(5)), second=int(time_m.group(6)))
            item['keyword'] = self.keyword
            ul = li.xpath('./ul/li/a/text()')
            if ul is not None:
                item['star'] = ul.extract_first()
            else:
                item['star'] = 0
            if item['star'] is None:
                item['star'] = 0
            item['refer'] = response.url
            m = re.search(r'illust_id=(\d+)$', item['link'])
            item['id'] = m.group(1)
            # print item
            # print self.save_thumbs
            if self.save_thumbs:
                yield item
            # print 'keyword' in item.fields

            if int(item['star']) >= self.save_star:
                if item['multi']:
                    yield scrapy.Request(self.manga_root + item['id'], meta={'cookiejar': response.meta['cookiejar'],
                                                                             'star': item['star'],
                                                                             'id': item['id']
                                                                             },
                                         callback=self.parse_manga
                                         )
                else:
                    yield scrapy.Request(self.single_root + item['id'], meta={'cookiejar': response.meta['cookiejar'],
                                                                              'star': item['star'],
                                                                              'id': item['id']
                                                                              },
                                         callback=self.parse_inner
                                         )

        self.current += 1
        if self.max_page == 0 or self.current <= self.max_page and next_page is not None:
            yield scrapy.Request(
                url=next_page,
                meta={'cookiejar': response.meta['cookiejar']},
                callback=self.parse
            )

    def parse_inner(self, response):
        root = response.selector
        image = root.xpath('//img[@class="original-image"]')
        if image is not None:
            src = image.xpath('@data-src').extract_first()
            item = BigImage()
            item['star'] = response.meta['star']
            item['id'] = response.meta['id']
            item['refer'] = response.url
            item['page'] = 0
            item['image_urls'] = [src, ]
            item['img_save_dir'] = self.img_save_dir
            yield item
        else:
            print 'error'

    def parse_manga(self, response):
        root = response.selector
        images = root.xpath('//img[@data-filter="manga-image"]/@data-src')
        if images is not None:
            page = 0
            for image in images.extract():
                item = BigImage()
                item['star'] = response.meta['star']
                item['id'] = response.meta['id']
                item['refer'] = 'http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=%s&page=%d' % (response.meta['id'], page)
                item['page'] = page
                item['image_urls'] = [image.replace('c/1200x1200/img-master', 'img-original').replace('_master1200', ''), ]
                item['img_save_dir'] = self.img_save_dir
                yield item
                page += 1
        else:
            print 'error'
