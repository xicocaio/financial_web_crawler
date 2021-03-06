import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from linyphiidae.spiders.wsj_news_spider import WSJNewsSpider
from linyphiidae.spiders.crypto_sitemap_spider import CryptoSitemapSpider

spider_classes = {
    'wsj_news': WSJNewsSpider,
    'crypto_sitemap': CryptoSitemapSpider
}


def run_crawler(abs_data_dir, mode, max_requests, end_time, start_time, website, stock_info, max_elems):
    # default values
    website = website if website else 'wsj_news'

    # The path seen from root, ie. from main.py
    settings_file_path = 'linyphiidae.settings'
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    process = CrawlerProcess(get_project_settings())
    process.crawl(spider_classes[website], mode, max_requests, end_time, start_time, stock_info, abs_data_dir,
                  max_elems)
    # process.start(stop_after_crawl=False)
    process.start()

    # runner = CrawlerRunner(get_project_settings())
    #
    # d = runner.crawl(spider_classes[website], mode, max_requests, end_time, start_time, stock_info, abs_data_dir,
    #                  max_elems)
    # d.addBoth(lambda _: reactor.stop())
    # reactor.run()
