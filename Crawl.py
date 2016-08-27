# encoding= UTF-8

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("pixiv")
    process.start()

print "Spider start"
main()
