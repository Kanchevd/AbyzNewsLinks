# Scrapy settings for abyznews project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'abyznews'

SPIDER_MODULES = ['abyznews.spiders']
NEWSPIDER_MODULE = 'abyznews.spiders'
LOG_LEVEL = 'ERROR'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'abyznews (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
	'abyznews.pipelines.AbyznewsPipeline': 100,

}