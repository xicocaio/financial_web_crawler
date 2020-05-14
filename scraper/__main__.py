# from jobs.scrap import scrap_market_watch
# from jobs.upload import load_to_gbq
# from jobs.query import run_all_queries
import os
import sys
import csv

from datetime import datetime
from crawler_manager import run_crawler
from csv_generator import generate_wsj_csv, generate_html_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR + '/data'
STOCK_LIST_DIR = BASE_DIR + '/companies_list.csv'


# generating dest dir path for storing scrapped data
def generate_dest_path(stock, crawl_type='api', website='wsj_news'):
    abs_dir_path = DATA_DIR + '/{}/{}/{}/'.format(crawl_type, website, stock.upper())

    # directory generation
    if abs_dir_path and not os.path.isdir(abs_dir_path):
        print('\n--- Creating target data subfolder ---\n')
        os.makedirs(abs_dir_path)

    return abs_dir_path


# validating the stocks
def validate_stock(stock):
    if not stock:
        raise ValueError('No stock selected')

    with open(STOCK_LIST_DIR, mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        allowed_stocks = (row['symbol'] for row in reader)

        if stock != 'list' and stock not in allowed_stocks:
            raise ValueError('\'{}\' stock not allowed, first add entry to "companies_list.csv"'.format(stock))

    return stock


# validating the crawl types
def validate_crawl_type(crawl_type):
    if crawl_type not in ['api', 'website']:
        raise ValueError('\'{}\' crawl type is invalid'.format(crawl_type))

    return crawl_type


# validating the avilable modes
def validate_mode(mode_option):
    if mode_option not in ['greedy']:
        raise ValueError('\'{}\' mode option is invalid'.format(mode_option))

    return mode_option


# validating date time format
def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        return date_str
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DDThh:mm:ss")


def get_stock_info(stock):
    with open(STOCK_LIST_DIR, mode='r') as infile:
        reader = csv.DictReader(infile, delimiter=';')

        stocks_dict = {row['symbol']: {'name': row['name'], 'symbol': row['symbol'], 'wsj_ticker': row['wsj_ticker']}
                       for row in reader if stock == 'list' or row['symbol'] == stock}

        return stocks_dict


def main(**kwargs):
    # default values
    step = kwargs.get('step') if 'step' in kwargs else 'all'  # allow: all, gen_csv
    max_requests = int(kwargs.get('max_requests')) if 'max_requests' in kwargs else None
    end_time = validate_date(kwargs.get('end_time')) if 'end_time' in kwargs else None
    start_time = validate_date(kwargs.get('start_time')) if 'start_time' in kwargs else None
    mode = validate_mode(kwargs.get('mode')) if 'mode' in kwargs else None  # modes: default, greedy
    stock = validate_stock(kwargs.get('stock'))
    max_elems = int(kwargs.get('max_elems')) if 'max_elems' in kwargs else 100
    crawl_type = validate_crawl_type(kwargs.get('crawl_type'))
    website = kwargs.get('website') if 'website' in kwargs else 'wsj_news'

    stock_info = get_stock_info(stock)
    abs_data_paths = {stock_symbol: generate_dest_path(stock=stock_symbol, crawl_type=crawl_type, website=website)
                      for stock_symbol in stock_info.keys()}

    if step == 'scrap' or step == 'all':
        run_crawler(abs_data_paths, mode, max_requests, end_time, start_time, website, stock_info, max_elems)

    if step == 'gen_csv' or step == 'all':
        for stock_symbol, info in stock_info.items():
            print('\n--- Starting csv generation of stock: {} ({}) ---\n'.format(info['name'], info['symbol'].upper()))

            if crawl_type == 'api':
                generate_wsj_csv(abs_data_paths, info)
            else:
                generate_html_csv(abs_data_paths, info)


if __name__ == '__main__':
    main(**dict(arg.replace('--', '').split('=') for arg in sys.argv[1:]))  # kwargs
