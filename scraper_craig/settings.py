# -*- coding: utf-8 -*-

# Scrapy settings for scraper_craig project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os
from scrapy.utils.project import project_data_dir


STORE_IMAGES = False
# if True, will use proxy
USE_PROXY = False
# LINK TO GENERATE REQUESTS FROM
ROOT_LINK = 'https://boston.craigslist.org/search/hhh'

WALKSCORE_API_KEY = '28e22315d2e853f1afe5db5423a4d6a8'

PROJECT_DIR = os.path.dirname(project_data_dir('scraper_craig'))
# csv file to save scraped items
CSV_FILEPATH = os.path.join(PROJECT_DIR, 'csv/Craiglist_Export.csv')
# Store images there
IMAGES_STORE = os.path.join(PROJECT_DIR, 'images')
# if True, scrapper saves images


# spider uses types to check if it's in the text, if static phrase is in text, it's added to item field
HOUSE_TYPES = ['apartment', 'condo', 'cottage/cabin',
               'duplex', 'flat', 'house', 'in-law',
               'loft', 'townhouse', 'manufactured',
               'assisted living', 'land']

PARKING_TYPES = ['carport', 'attached garage',
                 'detached garage', 'off-street parking',
                 'street parking', 'valet parking', 'no parking']

LAUNDRY_TYPES =['w/d in unit', 'w/d hookups', 'laundry in bldg',
                'no laundry on site', 'laundry on site']


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = \
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

BOT_NAME = 'scraper_craig'

SPIDER_MODULES = ['scraper_craig.spiders']
NEWSPIDER_MODULE = 'scraper_craig.spiders'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scraper_craig.middlewares.ScraperCraigSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware':50,
   'scraper_craig.middlewares.ProxyGrabberCheckerMiddleware': 101 if USE_PROXY else None,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 102,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scraper_craig.pipelines.ImageProcessor': 1 if STORE_IMAGES else None,
    'scraper_craig.pipelines.DuplicateChecker': 300,
}


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

