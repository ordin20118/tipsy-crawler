# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TastingNotesItem(scrapy.Item):
    nosing = scrapy.Field()
    tasting = scrapy.Field()
    finish = scrapy.Field()
    body = scrapy.Field()
    tannin = scrapy.Field()
    sweetness = scrapy.Field()
    acidity = scrapy.Field()

class DailyshotLiquorCrawlerItem(scrapy.Item):
    name_en = scrapy.Field()
    name_kr = scrapy.Field()
    abv = scrapy.Field()
    category_name = scrapy.Field()
    country_name = scrapy.Field()
    region_name = scrapy.Field()
    variety = scrapy.Field()
    tasting_notes = scrapy.Field()
    rating_avg = scrapy.Field()
    rating_count = scrapy.Field()
    pairing = scrapy.Field()
    price = scrapy.Field()
    image_url = scrapy.Field()
    description = scrapy.Field()
    tasting_notes = scrapy.Field()
    
