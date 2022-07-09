# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PstagItem(scrapy.Item):
    page_url = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    reward_amount = scrapy.Field()
    associated_organization = scrapy.Field()
    associated_location = scrapy.Field()
    about = scrapy.Field()
    image_url = scrapy.Field()
    date_of_birth = scrapy.Field()

