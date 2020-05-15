# -*- coding: utf-8 -*-

import json
import os

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

class StoreNewsPipeline(object):

    # generating dest dir path for storing scrapped data
    def generate_dest_path(self, abs_dest_path, new_folder):
        complete_new_path = abs_dest_path + new_folder

        # directory generation
        if complete_new_path and not os.path.isdir(complete_new_path):
            print('--- Creating target data subfolder ---\n')
            os.makedirs(complete_new_path)

        return complete_new_path

    def process_html(self, item, spider):
        # filename will be the start_time of the first_request in ISO format
        # considering only seconds
        # filename = spider.crawler.stats.get_value(
        #     'start_time').isoformat(timespec='seconds')
        # input_fname = spider.abs_data_dir + '{}.jl'.format(filename)

        # to get spider name
        # spider.name

        # creating file if non existent, and appending the json responses of
        # each request into the file
        # filename = response.url + '.html'

        # b'https://www.newsbtc.com/post-sitemap28.xml'
        website_name = 'https://www.newsbtc.com'
        url_name = item['url'].replace('https://www.newsbtc.com', '').strip('//').replace('/', '-')

        referer = item['url_referer'].replace('https://www.newsbtc.com', '').strip('//').replace('.xml', '/')

        complete_final_path = self.generate_dest_path(spider.abs_data_dir, referer)

        # do not forget to get the ref for the name as part of the date the crawl was run
        # filename = spider.crawler.stats.get_value(
        #     'start_time').isoformat(timespec='seconds')

        filename = url_name + '.html'
        input_fname = complete_final_path + filename
        with open(input_fname, 'wb') as f:
            f.write(item['body'])
        return item

    def process_json(self, item, spider):
        # filename will be the start_time of the first_request in ISO format
        # considering only seconds
        filename = spider.crawler.stats.get_value(
            'start_time').isoformat(timespec='seconds')
        input_fname = spider.abs_data_dir + '{}.jl'.format(filename)

        # to get spider name
        # spider.name

        # creating file if non existent, and appending the json responses of
        # each request into the file
        with open(input_fname, "a+") as file:
            json.dump(item, file)
            file.write('\n')

        return item

    def process_item(self, item, spider):
        if spider.name == 'wsj_news':
            return self.process_json(item, spider)
        elif spider.name == 'crypto_sitemap':
            return self.process_html(item, spider)
