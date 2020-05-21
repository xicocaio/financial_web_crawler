import scrapy
from scrapy.http import JsonRequest
from scrapy.spidermiddlewares.httperror import HttpError

import json

# 2500 seems to be the max number of elements on response, however, sometimes this length leads to errors
MAX_ALLOWED_ELEMENTS = 2250


class WSJNewsSpider(scrapy.Spider):
    name = "wsj_news"

    allowed_domains = ['api.wsj.net']
    initial_time = None
    reqs_number = 0

    # stock symbols follow the following examples of bitcoin and apple:
    # 'symb!~!US:BTCUSD!, !symb!~!US:AAPL'

    def __init__(self, mode, max_requests, end_time, start_time, stock_info, abs_data_paths, max_elems=100,
                 *args, **kwargs):
        super(WSJNewsSpider, self).__init__(*args, **kwargs)

        # there are only to modes, greedy and default
        if mode and mode == 'greedy':
            print(
                'WARNING: the greedy mode runs to exhausting all data available in the desired website about the specified stock this may lead to banishment if not done properly')
            self.max_requests = None
            self.end_time = None
            self.start_url = 'https://api.wsj.net/api/slinger/headlines/806/' + str(MAX_ALLOWED_ELEMENTS)
        else:
            self.max_requests = max_requests if max_requests else 2
            self.end_time = end_time if end_time else None  # oldest possible time
            self.start_url = 'https://api.wsj.net/api/slinger/headlines/806/' + str(max_elems)

        self.start_time = start_time if start_time else None  # time to start requests

        self.unprocessed_stock = stock_info.copy()
        self.current_stock_symbol, self.current_stock_info = self.unprocessed_stock.popitem()

        self.abs_data_paths = abs_data_paths.copy()
        self.abs_data_dir = self.abs_data_paths[self.current_stock_symbol]

        self.start_query_params = {
            'version': '3',
            'opProp': 'symb!~!' + self.current_stock_info['wsj_ticker']
        }

        if start_time:
            self.start_query_params['datetime'] = start_time
            self.start_query_params['direction'] = 'older'

    def start_requests(self):
        print('\n--- Starting crawl of stock: {} ({}) ---\n'.format(self.current_stock_info['name'],
                                                                    self.current_stock_info['symbol'].upper()))
        yield JsonRequest(url=self.start_url, data=self.start_query_params, dont_filter=False)

    def start_new_stock(self, response):
        if self.unprocessed_stock:
            self.current_stock_symbol, self.current_stock_info = self.unprocessed_stock.popitem()

            print('\n--- Starting crawl of stock: {} ({}) ---\n'.format(self.current_stock_info['name'],
                                                                        self.current_stock_info['symbol'].upper()))

            self.reqs_number = 0

            self.start_query_params = {
                'version': '3',
                'opProp': 'symb!~!' + self.current_stock_info['wsj_ticker']
            }

            self.abs_data_dir = self.abs_data_paths[self.current_stock_symbol]

            yield JsonRequest(url=response.url, data=self.start_query_params, dont_filter=False, callback=self.parse)

    def parse(self, response):
        if response.xpath("//*[contains(text(), 'timed out')]"):
            print('\n Timeout request {}: \n'.format(response))

        json_response = json.loads(response.body_as_unicode())

        self.reqs_number += 1

        # dealing with this HeadlinesResponse that is a placeholder for lists
        for json_list in json_response['HeadlinesResponse']:
            # the summary object is one to check to see if there is any more
            # response beyond a given date
            if 'Summary' in json_list:
                oldest_date_obj = min(json_list['Summary'], key=lambda x: x[
                    'CreateTimestamp']['Value'])

                doc_id = oldest_date_obj['DocumentIdUri'].split('/')[-1]
                oldest_res_date = oldest_date_obj['CreateTimestamp']['Value']

                yield {
                    'HeadlinesResponse': json_response['HeadlinesResponse'],
                }

                # condition for stopping is if max_requests was or max end time was reached
                can_stop = (self.max_requests and self.reqs_number >= self.max_requests) or (
                        self.end_time and oldest_res_date <= self.end_time)

                if not can_stop:
                    # updating params for next request
                    query_params = self.start_query_params.copy()
                    query_params['datetime'] = oldest_res_date
                    query_params['direction'] = 'older'

                    # This param seems to be useless. But the official website request uses it.
                    query_params['docid'] = doc_id

                    yield JsonRequest(url=response.url, data=query_params, dont_filter=False,
                                      callback=self.parse)
                # start new stock
                else:
                    yield from self.start_new_stock(response)
            else:
                yield from self.start_new_stock(response)

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
