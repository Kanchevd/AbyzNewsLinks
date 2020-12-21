import scrapy
import time
import re


class AbyzSpider(scrapy.Spider):
    name = 'abyz'
    allowed_domains = ['abyznewslinks.com']
    start_urls = ['http://www.abyznewslinks.com/allco.htm']
    pages = 0

    def parse(self, response):

        countries = response.xpath("(//table)[6]//a/@href").getall()
        yield from response.follow_all(countries, callback=self.parse_country)
        # yield scrapy.Request(url='http://www.abyznewslinks.com/uzbek.htm', callback=self.parse_country)

    def parse_country(self, response):
        header = response.xpath(
            "(//table)[4]//text()").getall()  # header table to determine if page has scrapable links
        header = [text.strip() for text in header if text.strip()]  # get only lines with text

        if header[0] != "Media Type":  # if if does not start with that, it has sublinks that need to be explored
            tables = response.xpath('//table')
            tables = tables[5:]  # first 5 tables never have links
            tables = [table for table in tables if table.xpath('.//a').get()]  # check if table has links
            for table in tables:
                links = table.xpath('.//a/@href').getall()  # get all links
                # visit all links and redirect them back to this function
                yield from response.follow_all(links, callback=self.parse_country)
                return

        header_dict = self.get_header_dictionary(header)  # if the is a valid header, get it as a dictionary

        self.pages += 1  # increment number of results
        path = response.xpath("(//table)[3]//text()").getall()  # table containing path
        # reformat path to desired format
        path = [re.sub('[(\n)?.!/;:>]', '', text) for text in path if text.strip() and text.strip() != '>']

        country = sub_national = ''  # used to later check if reassigned

        if len(path) >= 3:  # third name in the path is sub-region
            sub_region = path[2]
        else:
            sub_region = path[1]  # in case of UN and International

        if len(path) >= 4:  # fourth name in the path is country
            country = path[3]
            print(country + ' ' + str(self.pages))

        if len(path) >= 5:  # fifth name in the path is sub-national level
            sub_national = path[4]

        tables = response.xpath('//table')
        tables = tables[5:]  # first 5 tables don't contain useful links
        tables = [table for table in tables if table.xpath('.//a').get()]  # get the tables which have links
        for table in tables:
            # every table is a data type, table[0] is city/scope, table[1] is name + url, table[3] is media type, etc.

            city_scope = table.xpath('.//td')[0]
            city_scope_list = self.get_from_linebreaks(city_scope)
            # this function takes into account line breaks to line up all variables as in the original document
            print(city_scope_list)
            name_and_url = table.xpath('.//td')[1]

            # name and url have special similar functions to accurately insert line breaks as empty spaces
            name_list = self.get_names_from_linebreaks(name_and_url)
            url_list = self.get_urls_from_linebreaks(name_and_url)

            media_types = table.xpath('.//td')[2]
            media_types_list = self.get_from_linebreaks(media_types)
            media_types_list = self.decode(header_dict, media_types_list)
            print(media_types_list)
            media_focus = table.xpath('.//td')[3]
            media_focus_list = self.get_from_linebreaks(media_focus)
            media_focus_list = self.decode(header_dict, media_focus_list)

            language = table.xpath('.//td')[4]
            language_list = self.get_from_linebreaks(language)
            language_list = self.decode(header_dict, language_list)

            channels = table.xpath('.//td')[5]
            channels_list = self.get_from_linebreaks(channels)

            # Code for splitting double languages
            langs_to_split = {}
            for index, lang in enumerate(language_list):
                lang = lang.strip()
                if ' ' in lang:  # if there is a space, there are two language codes
                    temp_list = lang.split(' ')  # split them
                    langs_to_split[index] = []  #
                    for entry in temp_list:  # add them to a list
                        langs_to_split[index].append(entry)

            if langs_to_split:  # if there are any double languages
                for key in langs_to_split:
                    language_list.pop(key)  # remove the doubled string
                    language_list[key:key] = langs_to_split[key]  # add them in its place one by one

            # get the lowest number to ensure there are no out of range errors
            iterations = min(len(city_scope_list), len(name_list), len(language_list),
                             len(media_focus_list), len(media_types_list))

            for i in range(iterations):
                # remove unfinished lines
                if not media_types_list[i] or not media_focus_list[i] or not name_list[i] or not city_scope_list[i]:
                    continue

                source_dict = {}
                # check that every variable exists before adding it in the dictionary

                if sub_region:
                    source_dict['Sub-region'] = sub_region

                if country:
                    source_dict['Country'] = country

                if sub_national:
                    source_dict['Sub-national'] = sub_national

                if len(city_scope_list) > i - scope_skip:
                    source_dict['City/Scope'] = city_scope_list[i]

                if len(name_list) > i:
                    source_dict['Name'] = name_list[i]

                if len(url_list) > i:
                    source_dict['URL'] = url_list[i]

                if len(media_types_list) > i:
                    source_dict['Media Type'] = media_types_list[i]

                if len(media_focus_list) > i:
                    source_dict['Media Focus'] = media_focus_list[i]

                if len(channels_list) > i:
                    source_dict['Channel'] = channels_list[i]

                if len(language_list) > i:
                    source_dict['Language'] = language_list[i]

                yield source_dict

    @staticmethod
    def get_from_linebreaks(selector):
        # get text between linebreaks to line up variables
        selector_list = []
        line_breaks = 0
        empty_count = 0
        while empty_count < 3:  # signals end of variables
            text = selector.xpath(f".//*[count(preceding-sibling::br)={line_breaks}]/text()").getall()

            if not text:
                empty_count += 1
            else:
                empty_count = 0

            for item in text:
                item = item.replace("\n", " ")  # remove new lines from text
                selector_list.append(item)
            line_breaks += 1  # go to the next line break

        # handle the rare case of the first element being empty when it is not in reality
        if selector_list and not selector_list[0].strip():
            selector_list.pop(0)

        selector_list = [item.strip() for item in selector_list]  # strip unnecessary spaces
        # print(selector_list)
        return selector_list

    @staticmethod
    def get_names_from_linebreaks(selector):
        # similar to the function above, but for names
        selector_list = []
        follows_linebreak = False

        text = selector.xpath(f".//*[self::a or self::br]").getall()
        for element in text:
            if element.startswith("<a"):
                left_bracket = element.find('>')
                right_bracket = element.find('<', 1)
                name = element[left_bracket + 1:right_bracket]
                name = name.replace("\n", " ")
                selector_list.append(name)
                follows_linebreak = False
            else:
                if follows_linebreak:
                    selector_list.append(" ")
                follows_linebreak = True

        # print(selector_list)
        return selector_list

    @staticmethod
    def get_urls_from_linebreaks(selector):
        # similar to the function above, but for URLs
        selector_list = []
        follows_linebreak = False

        text = selector.xpath(f".//*[self::a or self::br]").getall()

        for element in text:
            if element.startswith("<a"):
                left_quote = element.find('"')
                right_quote = element.find('"', left_quote + 1)
                name = element[left_quote + 1:right_quote]
                selector_list.append(name)
                follows_linebreak = False
            else:
                if follows_linebreak:
                    selector_list.append(" ")
                follows_linebreak = True

        # print(selector_list)
        return selector_list

    @staticmethod
    def get_header_dictionary(table):
        # Turns the header table into a dictionary
        table = table[:-1]
        header_dict = {}
        for element in table:
            dash_index = element.find('-')
            if dash_index != -1:
                header_dict[element[:dash_index]] = element[dash_index + 1:]
        return header_dict

    @staticmethod
    # Turns a list of abbreviations and replaces it with a list of the meanings
    def decode(header_dict, coded):
        decoded = []
        for element in coded:
            if element in header_dict.keys():
                decoded.append(header_dict[element])
            else:
                decoded.append(element)

        return decoded
