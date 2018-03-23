import csv
import json
from scrapy import Spider
from scrapy import Request
from scrapy.utils.project import get_project_settings
from scraper_craig.items import Scores
from scrapy.loader import  ItemLoader
from scrapy.exceptions import CloseSpider
from urllib import parse
import pandas as pd
setts = get_project_settings()


class ScoresSpider(Spider):
    name = 'scores_spider'
    API_KEY = setts['WALKSCORE_API_KEY']
    BASE_URL = 'http://api.walkscore.com/score?format=json'
    score_dict ={}

    def parse_scores(self, response):
        jsonresponse = json.loads(response.body_as_unicode())
        if self.check_ws_api_status(jsonresponse['status'])==1:
            return
        d_key = int(response.meta.get('craig_id'))
        d_items = {}
        d_items.update(dict(walkscore=jsonresponse['walkscore']))
        for itm in ('bike', 'transit'):
            try:
                d_items.update({itm+'score':jsonresponse[itm]['score']})
            except KeyError:
                d_items.update({itm+'score': ''})
        self.score_dict.update({d_key:d_items})

    def start_requests(self):
        self.lines_read = 0
        self.ws_aviliable_c =0
        with open(setts["CSV_FILEPATH" ], mode='r', encoding='utf8') as csv_file:
            reader = csv.reader(csv_file)
            h_line = reader.__next__()
            id_loc = h_line.index('Craiglist_PostingID')
            address_loc = h_line.index('Address')
            lat_loc = h_line.index('Latitude')
            lon_loc = h_line.index('Longitude')
            walk_score_loc = h_line.index('Walkscore')
            for line in reader:
                self.lines_read+=1
                if line[walk_score_loc]:
                    continue
                r_url = self.BASE_URL
                r_url+='&address=%s' % parse.quote(line[address_loc])
                r_url+='&lat=%s' % line[lat_loc]
                r_url+='&lon=%s' % line[lon_loc]
                r_url+='&transit=1&bike=1&wsapikey=%s' % self.API_KEY
                self.ws_aviliable_c+=1
                yield Request(url=r_url, callback=self.parse_scores, meta ={'craig_id':line[id_loc]})

    def closed(self, reason):
        df = pd.read_csv(setts['CSV_FILEPATH'], header=0,
                         index_col='Craiglist_PostingID')
        for craig_id in self.score_dict.keys():
            df.loc[craig_id, 'Walkscore'] = self.score_dict[craig_id]['walkscore']
            df.loc[craig_id, 'BikeScore'] = self.score_dict[craig_id]['bikescore']
            df.loc[craig_id, 'TransitScore'] = self.score_dict[craig_id]['transitscore']
        df.to_csv(setts['CSV_FILEPATH'])



        pass


    def check_ws_api_status(self, status):
        """
        200 	1 	Walk Score successfully returned.
        200 	2 	Score is being calculated and is not currently available.
        404 	30 	Invalid latitude/longitude.
        500 series 	31 	Walk Score API internal error.
        200 	40 	Your WSAPIKEY is invalid.
        200 	41 	Your daily API quota has been exceeded.
        403 	42 	Your IP address has been blocked.
        :param status:
        :return:
        """
        if status == 1:
            pass
        if status == 2:
            self.logger.info('score is being calculated will be aviliable later')
            return 1
        if status == 30:
            self.logger.info('Invalid latitude/longitude, ignoring')
            return 1
        if status == 31:
            pass
        if status == 40:
            self.logger.error(" API_KEY IS INVALID ")
            raise CloseSpider('API KEY IS INVALID')
        if status == 41:
            self.logger.error('Your daily API quota has been exceeded')
            raise  CloseSpider('Your have reached quota today, change API_KEY or try later')
        if status == 42:
            self.logger.error('Your IP address has been blocked.')
            raise CloseSpider('Your IP address has been blocked, change ip or try later')





