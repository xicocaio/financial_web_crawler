# -*- coding: utf-8 -*-

import json


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class StoreNewsPipeline(object):

    def process_item(self, item, spider):
        # filename will be the start_time of the first_request in ISO format
        # considering only seconds
        filename = spider.crawler.stats.get_value(
            'start_time').isoformat(timespec='seconds')
        input_fname = spider.abs_data_dir + '/{}.jl'.format(filename)

        # creating file if non existent, and appending the json responses of
        # each request into the file
        with open(input_fname, "a+") as file:
            json.dump(item, file)
            file.write('\n')

        return item
