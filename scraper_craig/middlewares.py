# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.extensions.closespider import *
from scrapy.http import Request, Response, TextResponse
from urllib.request import urlopen
from random import choice
import logging
from twisted.internet.error import ConnectionRefusedError, TimeoutError, TCPTimedOutError, ConnectError
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.exceptions import CloseSpider
# class ScraperCraigSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Response, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         proxy_list = []
#         spider.logger.info('Spider opened: %s' % spider.name)

class ProxyGrabberCheckerMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def stop(self):
        pass

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        self._update_proxy(request, spider)
        #  Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        if response.status == 403 and request.meta['proxy']:
            self._change_bad_proxy(request)
            return request

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.
        # 111 = connection refused
        if isinstance(exception, ConnectionRefusedError):
            self._change_bad_proxy(request)
            return request
        elif isinstance(exception, TimeoutError):
            self._change_bad_proxy(request)
            return request
        elif isinstance(exception, TCPTimedOutError):
            self._change_bad_proxy(request)
            return request
        elif isinstance(exception, TunnelError):
            self._change_bad_proxy(request)
            return request
        elif isinstance(exception, ConnectError):
            self._change_bad_proxy(request)
            return request

        print('unhandled exception')


        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass


    def spider_opened(self, spider):
        self.proxy_list = self.grab_proxy()
        spider.logger.info('Spider opened: %s' % spider.name)

    def grab_proxy(self):
        url = 'https://webanetlabs.net/publ/24'
        resp = TextResponse(url=url, body=urlopen(url).read())
        # grab the rel_path of the newest post with free proxy
        relative_path = resp.xpath('//div[@class ="eTitle"][1]/a[1]/@href').extract_first()
        new_url = '/'.join(url.split('/')[:-1]) + relative_path
        resp = TextResponse(url=url, body=urlopen(new_url).read())
        proxy_list = resp.xpath('//span[@itemprop="articleBody"]/p/text()').extract()
        proxy_list= [x.replace('\n', '') for x in proxy_list if len(x) > 5]
        logging.debug('PROXY LIST GRABBED:\n %s'%proxy_list)
        return proxy_list

    def _update_proxy(self,request, spider):
        if not self.proxy_list:
            spider.crawler.engine.close_spider(spider, 'No more proxies left, shutting down')
            return
        proxy = choice(self.proxy_list)
        request.meta.update({'proxy': 'http://%s' % proxy,
                             'proxy_ip': proxy,
                             'dont_retry':True,
                             'download_timeout':7,
                             })

    def _change_bad_proxy(self,request):
        if self.proxy_list:
            logging.info('%s bad proxy! changing proxy, filtering...' % (request.meta['proxy_ip'], ))
            if request.meta['proxy_ip'] in self.proxy_list: # check if proxy was not deleted yet
                self.proxy_list.remove(request.meta['proxy_ip'])
        else:
            pass






