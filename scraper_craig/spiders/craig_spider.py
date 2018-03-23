# scrapy spider
import scrapy
import csv
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import  ItemLoader
from scraper_craig.items import  House
from scrapy.loader.processors import TakeFirst, Compose, Join
from scrapy.utils.project import get_project_settings
from w3lib.html import remove_tags
from scrapy.exceptions import CloseSpider



class CraigSpider(CrawlSpider):
    """
    main class that have rules and functions to process links/pages
    """
    start_urls = []
    name = 'craig_spider'
    # 1st rule just follows links in certain place
    # 2nd rule goes
    counter = 1
    count_links=0
    link_counter =0
    debug_links = []
    rules = (
             Rule(link_extractor=LinkExtractor(restrict_xpaths='/html/body/section/form/div[3]/div[3]/span[2]/a[3]', ),
                  follow=True, process_links='test_count'),
             Rule(link_extractor=LinkExtractor(restrict_xpaths='/html/body/section/form/div[4]/ul/li', ),
                  callback='parse_product',
                  process_links = 'check_titles'),
            # sometimes grabs link from search =/ price+-
    )

    def test_count(self, links):
        self.link_counter +=1
        self.debug_links.append(links)
        return links

    def check_titles(self, links):
        self.count_links+=1
        for link in links:
            # remove no-items links

            title_part = link.url.split('/')[-2]
            if title_part in self.titles_pool:
                self.logger.debug("Title %s already in database, passed" % title_part)
                links.pop(links.index(link))
            else:
                self.titles_pool.add(title_part)
        return links

    def __init__(self,setts = None, *args, **kwargs):
        super(CraigSpider, self).__init__(*args, **kwargs)

        if setts == None:
            setts = get_project_settings()
        self.root_link=setts['ROOT_LINK']
        if 'craigslist.org/search/' in self.root_link:
            for x in range(60):
                self.start_urls.append(
                    self.root_link + '?min_price=%s&max_price=%s' % (x * 100 + 1, x * 100 + 100))
            self.start_urls.append(self.root_link + '?min_price=6001&max_price=10000000')  # always less then 2500 res
        else:
            self.logger.error('"%s" - incorrect link, please try again'% self.root_link)
        self.titles_pool = self.get_titles_pool(setts['CSV_FILEPATH'])


    def parse_product(self,response):
        if 'craigslist.org/search' in response.url:
            return
        house = ItemLoader(item = House(), response = response)
        house.default_output_processor=Compose(lambda x:x[0])
        house.add_xpath('craiglist_postingid', '//p[@class="postinginfo"]',re='post id: ([0-9]*)')
        house.add_value('url', response.url)
        house.add_xpath('craiglist_postingdate', '/html/body/section/section/section/div[2]/p[2]/time/@datetime',
                       re = '\d\d\d\d-\d\d-\d\d')
        house.add_xpath('address', '//div[@class="mapaddress"]/text()')
        house.add_xpath('neighborhood', '/html/body/section/section/h2/span/small/text()')
        house.add_xpath('rent', '/html/body/section/section/h2/span[2]/span[1]/text()', re='\$(\d*)',)
        house.add_xpath('title','//*[@id="titletextonly"]/text()')
        house.add_xpath('bedrooms', '/html/body/section/section/section/div[1]/p[1]/span[1]/b[1]/text()', re='(\d*)BR')
        house.add_xpath('bathrooms', '/html/body/section/section/section/div[1]/p[1]/span[1]/b[2]/text()', re='(\d*)Ba')
        selector_list = response.xpath('/html/body/section/section/section/div[1]/p[@class="attrgroup"]/span')
        self.parse_sqfeets(loader=house,
                           selector_list=selector_list,)
        self.item_from_text(field_name='laundry',
                            loader=house,
                            selector_list=selector_list,
                            items_list=self.settings['LAUNDRY_TYPES'])
        self.item_from_text(field_name='housing_type',
                            loader=house,
                            selector_list=selector_list,
                            items_list=self.settings['HOUSE_TYPES'],)
        self.item_from_text(field_name='parking',
                            loader=house,
                            selector_list=selector_list,
                            items_list=self.settings['PARKING_TYPES'])

        house.add_xpath('description',
                        '//*[@id="postingbody"]', Join(), Compose(remove_tags, self._remove_qr_part)
                        )
        house.add_xpath('latitude', '//*[@id="map"]/@data-latitude')
        house.add_xpath('longitude', '//*[@id="map"]/@data-longitude')
        house.add_xpath('image_urls','//div[@id="thumbs"]/a/@href')
        self.logger.info('ITEM number >%s< scraped' % self.counter)
        self.counter +=1
        return house.load_item()


    def parse_sqfeets(self, loader, selector_list):
        for selector_item in selector_list:
            extracted = selector_item.extract()
            if '>ft<' in extracted:
                loader.add_value('sqfeet', selector_item.re('(\d*)</b>ft'))


    def item_from_text(self, field_name, loader, items_list, selector_list):
        """method to add items if the following phrase from the list was found
        somewhere in the selectors pathes"""
        extracted = str(selector_list.extract()).lower()
        for item in items_list:
            if item in extracted:
                loader.add_value(field_name, item)
                break

    def get_titles_pool(self, csv_filepath):
        titles_pool = set()
        with open(file=csv_filepath, encoding='utf8') as csv_file:
            reader=csv.reader(csv_file)
            # read header (1) line
            url_loc = reader.__next__().index('URL')
            for line in reader:
                if not line:
                    continue
                title = line[url_loc].split('/')[-2]
                titles_pool.add(title)
        return titles_pool

    def _remove_qr_part(self, string):
        string = string.replace(
            '\n        \n            QR Code Link to This Post\n            \n        \n',
            ''
        )
        return string

    def close(self, spider, reason):
        self.logger.info('Links walked : %s'% self.count_links)
        for link in self.debug_links:
            self.logger.info(link)