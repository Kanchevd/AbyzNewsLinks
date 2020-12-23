# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AbyznewsItem(scrapy.Item):
    country = scrapy.Field()
    sub_region = scrapy.Field()
    sub_national = scrapy.Field()
    city_scope = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    media_type = scrapy.Field()
    media_focus = scrapy.Field()
    channel = scrapy.Field()
    language = scrapy.Field()

