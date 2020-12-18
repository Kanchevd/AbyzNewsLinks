import scrapy
import time


class AbyzSpider(scrapy.Spider):
    name = 'abyz'
    allowed_domains = ['abyznewslinks.com']
    start_urls = ['http://www.abyznewslinks.com/allco.htm']

    def parse(self, response):
        filename = 'file.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        countries = response.xpath("(//table)[6]//a/@href").getall()
        for country in countries:
            print(country)
