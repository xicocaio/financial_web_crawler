# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# NOTE: this item class are just containers, however, they are implemented in such a way that we use
# them as a dict, and there is just a simple under the hood auto check for avoiding typos
# As these container does not seem to work as a proper object, and there is no real advantage in using in this way
# we are going to yield the dict directly

# class HtmlItem(scrapy.Item):
#     url = scrapy.Field()
#     body = scrapy.Field()
#     url_referer = scrapy.Field()

# class JsonItem(scrapy.Item):
#     headlines_response = scrapy.Field()
