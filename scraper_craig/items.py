# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Compose, Identity



class House(scrapy.Item):
    craiglist_postingid = scrapy.Field(input_processor=TakeFirst(),
                                       output_processor=Compose(lambda x:int(x[0]))) # transfering to integer
    url = scrapy.Field()
    craiglist_postingdate = scrapy.Field(output_processor=Compose(lambda x:str(x[0])))
    neighborhood = scrapy.Field()
    address = scrapy.Field()
    housing_type = scrapy.Field()
    rent = scrapy.Field()
    title = scrapy.Field()
    bedrooms = scrapy.Field(output_processor=Compose(lambda x:str(x[0])))
    bathrooms = scrapy.Field(output_processor=Compose(lambda x:str(x[0])))
    sqfeet = scrapy.Field()
    description = scrapy.Field(output_processor = Identity())
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    laundry = scrapy.Field()
    parking = scrapy.Field()
    walkcore = scrapy.Field()
    transitscore = scrapy.Field()
    bikescore = scrapy.Field()
    image_urls = scrapy.Field(output_processor = Identity())
    images = scrapy.Field()

    pass

class Scores(scrapy.Item):
    """
    item used to access and work with WalkScore
    """
    craig_id = scrapy.Field(input_processor = Compose(lambda x:int(x[0])))
    walkscore = scrapy.Field(input_processor=TakeFirst())
    transitscore = scrapy.Field(input_processor=TakeFirst())
    bikescore = scrapy.Field(input_processor=TakeFirst())

