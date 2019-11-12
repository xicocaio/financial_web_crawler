# from jobs.scrap import scrap_market_watch
# from jobs.upload import load_to_gbq
# from jobs.query import run_all_queries
import os
import sys
from datetime import datetime

from crawler_manager import run_crawler
from csv_generator import generate_wsj_csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR + '/data'


# generating dir path for storing scrapped data
def generate_dir(stock, website='wsj_news'):
    abs_dir_path = DATA_DIR + '/{}/{}/'.format(website, stock.upper())

    # directory generation
    if abs_dir_path and not os.path.isdir(abs_dir_path):
        print('--- Creating target data subfolder ---\n')
        os.makedirs(abs_dir_path)

    return abs_dir_path


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


def main(**kwargs):
    # default values
    step = kwargs.get('step') if 'step' in kwargs else 'all'
    max_requests = int(kwargs.get('max_requests')) if 'max_requests' in kwargs else None
    end_time = validate_date(kwargs.get('end_time')) if 'end_time' in kwargs else None
    start_time = validate_date(kwargs.get('start_time')) if 'start_time' in kwargs else None
    mode = validate_mode(kwargs.get('mode')) if 'mode' in kwargs else None
    stock = kwargs.get('stock') if 'stock' in kwargs else 'btcusd'
    max_elems = int(kwargs.get('max_elems')) if 'max_elems' in kwargs else 100

    abs_data_dir_path = generate_dir(stock=stock)

    if step == 'scrap' or step == 'all':
        run_crawler(abs_data_dir_path, mode, max_requests, end_time, start_time, kwargs.get('website'),
                    stock, max_elems)
    if step == 'gen_csv' or step == 'all':
        generate_wsj_csv(abs_data_dir_path, stock)


if __name__ == '__main__':
    main(**dict(arg.replace('--', '').split('=') for arg in sys.argv[1:]))  # kwargs
