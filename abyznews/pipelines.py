import sqlite3
from datetime import datetime


class AbyznewsPipeline:
    conn = sqlite3.connect('abyz.db')
    cursor = conn.cursor()
    url_list = None
    item_list_set = {'sub_region', 'country', 'sub_national',
                     'city_scope', 'name', 'url', 'media_type',
                     'media_focus', 'channel', 'language'}

    start_time = datetime.now()
    count_items = 1

    def open_spider(self, spider):
        print('start')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS `Abyznews` (
                            country varchar(100),
                            sub_region varchar(100),
                            sub_national varchar(100),
                            city_scope varchar(100),
                            name varchar(100),
                            url text,
                            media_type varchar(100),
                            media_focus varchar(100),
                            channel varchar(100),
                            language varchar(100),
                            date_added datetime
                            )''')
        self.conn.commit()

        self.cursor.execute(f"select distinct url from `Abyznews`")
        url_list = self.cursor.fetchall()
        self.url_list = [url[0] for url in url_list]

    def process_item(self, item, spider):

        for field in self.item_list_set:
            item.setdefault(field, '')

        country = item['country']
        sub_region = item['sub_region']
        sub_national = item['sub_national']
        city_scope = item['city_scope']
        name = item['name']
        url = item['url']
        media_type = item['media_type']
        media_focus = item['media_focus']
        channel = item['channel']
        language = item['language']

        # self.cursor.execute(f"select * from `Abyznews` where url = '{url}'")
        # self.url_list = self.cursor.fetchall()

        if url not in self.url_list:
            self.cursor.execute(f"""insert into `Abyznews`
                    (`country`, `sub_region`, `sub_national`, `city_scope`, `name`, 
                    `url`, `media_type`, `media_focus`, `channel`, `language`, date_added)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now') )""", (country, sub_region, sub_national, city_scope,
                                                                             name, url, media_type, media_focus, channel, language))
            self.conn.commit()

            self.count_items += 1

        return item

    def close_spider(self, spider):
        print(f'{self.count_items} new records, Elapsed time: {datetime.now() - self.start_time}')
        self.cursor.close()
        self.conn.close()
