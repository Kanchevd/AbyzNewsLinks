import scrapy


class AbyzSpider(scrapy.Spider):
    name = 'abyz'
    allowed_domains = ['abyznewslinks.com']
    start_urls = ['http://abyznewslinks.com/']

    def parse(self, response):
        pass
