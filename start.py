from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scraper_craig.spiders.craig_spider import  CraigSpider
from scraper_craig.spiders.scores_spider import  ScoresSpider
import logging
#
setts =  get_project_settings()
setts['LOG_LEVEL']=logging.INFO
a = CrawlerProcess(settings=setts)
a.crawl(CraigSpider())
a.start()


# This is scraper for craiglists


# Also there is a little GUI to make it more user friendly

# THANKS :)
