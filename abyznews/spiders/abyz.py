import scrapy
import time
import re


class AbyzSpider(scrapy.Spider):
    name = 'abyz'
    allowed_domains = ['abyznewslinks.com']
    start_urls = ['http://www.abyznewslinks.com/allco.htm']
    """
    Done:
    Sub-region
    Country
    Sub-national
    City/Scope
    
    Sub-region : Northern Europe - Path
    Country : United Kingdom- Path
    Sub-national : East Midlands - Path (optional)
    City : Derbyshire - ?
    Scope - National or Local(if city) - Row
    Name - Row
    Url - Row
    Type - Row - shortened, full in header
    Focus - Row - shortened, full in header
    Language - Row - shortened, full in header
    Channel - Row - shortened, full in header

    """
    pages = 0

    # sources = []

    def parse(self, response):
        """
        countries = response.xpath("(//table)[6]//a/@href").getall()
        for country in countries:
            print(country)

        yield from response.follow_all(countries, callback=self.parse_country)
        """
        yield scrapy.Request(url='http://www.abyznewslinks.com/uzbek.htm', callback=self.parse_country)

    def parse_country(self, response):
        header = response.xpath("(//table)[4]//text()").getall()
        header = [text for text in header if text.strip()]
        if header[0] != "Media Type":
            tables = response.xpath('//table')
            tables = tables[5:]
            tables = [table for table in tables if table.xpath('.//a').get()]
            for table in tables:
                links = table.xpath('.//a/@href').getall()
                yield from response.follow_all(links, callback=self.parse_country)
                return

        path = response.xpath("(//table)[3]//text()").getall()
        path = [text for text in path if text.strip() and text.strip() != '>']
        path = [re.sub('[(\n)?.!/;:>]', '', text) for text in path]
        region = path[1]
        statement = f'Region:{region}'

        sub_region = country = sub_national = ''

        if len(path) >= 3:
            sub_region = path[2]
            statement += f' Sub-Region:{sub_region}'

        if len(path) >= 4:
            country = path[3]
            statement += f' Country:{country}'

        if len(path) >= 5:
            sub_national = path[4]
            statement += f' Sub-national:{sub_national}'

        tables = response.xpath('//table')
        tables = tables[5:]
        tables = [table for table in tables if table.xpath('.//a').get()]
        for table in tables:
            city_scope = table.xpath('.//td')[0]
            city_scope_list = self.get_from_linebreaks(city_scope)

            name_and_url = table.xpath('.//td')[1]
            name_list = self.get_from_linebreaks(name_and_url)
            name_list = [name for name in name_list if name.strip()]

            url_list = self.get_from_linebreaks(name_and_url, attr='@href')

            media_types = table.xpath('.//td')[2]
            media_types_list = self.get_from_linebreaks(media_types)

            media_focus = table.xpath('.//td')[3]
            media_focus_list = self.get_from_linebreaks(media_focus)

            language = table.xpath('.//td')[4]
            language_list = self.get_from_linebreaks(language)

            channels = table.xpath('.//td')[5]
            channels_list = self.get_from_linebreaks(channels)

            name_skip = 0
            for i in range(len(city_scope_list)):

                if media_types_list[i] == " ":
                    if city_scope_list[i].strip() or channels_list[i].strip():
                        print(city_scope_list[i])
                        name_skip += 1

                    print("SKIPPING")
                    continue

                if len(name_list) + name_skip <= i:
                    break

                source_dict = {'country': country,
                               'sub-region': sub_region,
                               'sub-national': sub_national,
                               'city / scope': city_scope_list[i],
                               'name': name_list[i - name_skip],
                               'url': url_list[i - name_skip],
                               'media_type': media_types_list[i],
                               'media_focus': media_focus_list[i],
                               'language': language_list[i], }

                if len(channels_list) > i:
                    source_dict['channel'] = channels_list[i]

                yield source_dict

        self.pages += 1

    def get_from_linebreaks(self, selector, attr='text()'):
        selector_list = []
        line_breaks = 0
        empty_count = 0
        while empty_count < 3:
            text = selector.xpath(f".//*[count(preceding-sibling::br)={line_breaks}]/{attr}").getall()

            for i in range(len(text)):
                text[i] = text[i].replace("\n", " ")
            if not text:
                empty_count += 1
            else:
                empty_count = 0

            if line_breaks == 0 and selector.xpath('.//a').get() and len(text) >= 2 and text[0] == ' ' and text[1]:
                selector_list.append(text[1])
            else:
                for item in text:
                    selector_list.append(item)
            line_breaks += 1
        return selector_list
