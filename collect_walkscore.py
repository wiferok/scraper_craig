from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scraper_craig.spiders.craig_spider import  CraigSpider
from scraper_craig.spiders.scores_spider import  ScoresSpider
import logging

setts =get_project_settings()
a = CrawlerProcess(settings=setts)
new_walkscore_api_key = ''
if new_walkscore_api_key:
    setts['WALKSCORE_API_KEY'] = new_walkscore_api_key
s = ScoresSpider()
s.custom_settings = setts
a.crawl(s)
a.start()