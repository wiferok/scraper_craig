# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pandas as pd
import os
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class DuplicateChecker(object):

    def __init__(self, csv_export_filepath):
        self.export_file = csv_export_filepath
        self.id_pool = set(pd.read_csv(filepath_or_buffer=csv_export_filepath,
                                       header=0,
                                       index_col=['Craiglist_PostingID']).index.astype(int))

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        #
        keys_order = [u'craiglist_postingid','url', 'craiglist_postingdate', 'neighborhood', 'address', 'housing_type',
                      'rent', 'title', 'bedrooms', 'bathrooms', 'sqfeet', 'description',
                      'latitude', 'longitude', 'laundry', 'parking', ]

        def _fill_nans(item):
            # set NaN value for empty fields
            for key in keys_order:
                try:
                    item[key]
                except KeyError:
                    item[key] = ''

        id = item['craiglist_postingid']
        if id in self.id_pool:
            # raise DropItem('The item already in database id=%s' % id)
            pass
        # count each processed item
        else:
            _fill_nans(item)
            self.id_pool.add(id)
            f = open(self.export_file, mode='ab')
            self.exporter = CsvItemExporter(f, include_headers_line=False, fields_to_export=keys_order,lineterminator='\n' )
            self.exporter.start_exporting()
            self.exporter.export_item(item)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(csv_export_filepath=crawler.settings.get('CSV_FILEPATH'))



class ImageProcessor(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        address = request.meta.get('address')
        craig_id = request.meta.get('craiglist_postingid')
        n=1
        while os.path.isfile('images/%s - %s_%s.jpg' % (craig_id, address, n)):
            n+=1
        path = '%s - %s_%s.jpg' % (craig_id, address, n)
        return path


    def get_media_requests(self, item, info):
        try:
            meta = {'craiglist_postingid': item['craiglist_postingid'],
                    'address': item['address']}
        except KeyError:
            meta = {'craiglist_postingid': item['craiglist_postingid'],
                    'address': ''}
        return [Request(x, meta=meta) for x in item.get(self.images_urls_field, [])]

