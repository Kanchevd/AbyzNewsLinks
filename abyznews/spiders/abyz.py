import scrapy
import time
import re

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

        yield from response.follow_all(countries, callback=self.parse_country)

    def parse_country(self, response):
        path = response.xpath("(//table)[3]//text()").getall()
        path = [text for text in path if text.strip() and text.strip() != '>']
        path = [re.sub('[(\n)?.!/;:>]', '', text) for text in path]
        if len(path) < 3:
            print(path[-1] + ' SECOND')
            return

        if len(path) == 3:
            print(path[-1] + ' THIRD')
            return

        country = path[3]

        header = response.xpath("(//table)[4]//text()").getall()
        header = [text for text in header if text.strip()]
        status = 'Scrape now' if header[0] == "Media Type" else 'Go Further'

        if status == 'Go Further':
            print(country + ' ' + status)
