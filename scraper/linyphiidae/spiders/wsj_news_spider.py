import scrapy
from scrapy.http import JsonRequest

import json

SYMBOLS_DICT = {
    'btcusd': 'symb!~!US:BTCUSD',
    'aapl': 'symb!~!US:AAPL',
    'sp500': 'symb!~!US:SPX'
}


class WSJNewsSpider(scrapy.Spider):
    name = "wsj_news"

    allowed_domains = ['api.wsj.net']
    initial_time = None
    reqs_number = 0

    # for adding more than one use ',!', example:
    # 'symb!~!US:BTCUSD!,!symb!~!US:AAPL'

    def __init__(self, mode, max_requests, end_time, start_time, abs_data_dir='', stock='btcusd', max_elems=100, *args,
                 **kwargs):
        super(WSJNewsSpider, self).__init__(*args, **kwargs)

        # there are only to modes, greedy and default
        if mode and mode == 'greedy':
            print(
                'WARNING: the greedy mode runs to exhausting all data available in the desired website about the specified stock this may lead to banishment if not done properly')
            self.max_requests = None
            self.end_time = None
            self.start_url = 'https://api.wsj.net/api/slinger/headlines/806/' + str(2500)  # tested max number of elements on response
        else:
            self.max_requests = max_requests if max_requests else 2
            self.end_time = end_time if end_time else None  # oldest possible time
            self.start_time = start_time if start_time else None  # time to start requests
            self.start_url = 'https://api.wsj.net/api/slinger/headlines/806/' + str(max_elems)

        self.stock = stock
        self.abs_data_dir = abs_data_dir

        self.start_query_params = {
            'version': '3',
            'opProp': SYMBOLS_DICT[self.stock]
        }

        if start_time:
            self.start_query_params['datetime'] = start_time
            self.start_query_params['direction'] = 'older'

    def start_requests(self):
        yield JsonRequest(url=self.start_url, data=self.start_query_params)

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())

        self.reqs_number += 1

        # dealing with this HeadlinesResponse that is a placeholder for lists
        for json_list in json_response['HeadlinesResponse']:
            # the sumamry object is one to check to see if there is any more
            # response beyond a given date
            if json_list['Summary']:
                oldest_date_obj = min(json_list['Summary'], key=lambda x: x[
                    'CreateTimestamp']['Value'])

                doc_id = oldest_date_obj['DocumentIdUri'].split('/')[-1]
                oldest_res_date = oldest_date_obj['CreateTimestamp']['Value']

                yield {
                    'HeadlinesResponse': json_response['HeadlinesResponse'],
                }

                # conidtion for stopping is if max_requests was or max end time was reached
                can_stop = (self.max_requests and self.reqs_number >= self.max_requests) or (
                        self.end_time and oldest_res_date <= self.end_time)

                if not can_stop:
                    # updating params for next request
                    query_params = self.start_query_params.copy()
                    query_params['datetime'] = oldest_res_date
                    query_params['direction'] = 'older'

                    # This param seems to be useless. But the official website request uses it.
                    query_params['docid'] = doc_id

                    yield JsonRequest(url=response.url, data=query_params,
                                      callback=self.parse)
