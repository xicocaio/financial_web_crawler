import scrapy


# from scrapy.spiders import Rule
# from scrapy.linkextractors import LinkExtractor
#
# from lxml import etree


class CryptoSitemapSpider(scrapy.spiders.SitemapSpider):
    name = "crypto_sitemap"

    allowed_domains = ['www.newsbtc.com']
    sitemap_urls = ['https://www.newsbtc.com/sitemap_index.xml']
    # sitemap_follow = ['^(.*?)\/post-sitemap[0-9]+.xml']

    # add another rule to pages to be crawled, according to the date being in the name or not
    # https://regex101.com
    sitemap_follow = ['^(.*?)/post-sitemap[0-9]+.xml']

    # sitemap_follow = ['^(.*?)\/post-sitemap28.xml']

    # sitemap_rules = [('^(.*?)/post-sitemap[0-9].xml', 'parse_item')]

    # https: // www.newsbtc.com / post - sitemap2.xml

    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).
    #     # Rule(LinkExtractor(allow=('category\.php', ), deny=('subsection\.php', ))),
    #
    #     # Extract links matching 'item.php' and parse them with the spider's method parse_item
    #     Rule(LinkExtractor(allow=('^(.*?)\/post-sitemap[0-9].xml', )), callback='parse_item'),
    # )

    def __init__(self, mode, max_requests, end_time, start_time, stock_info, abs_data_dir, max_elems=100, *args,
                 **kwargs):
        super(CryptoSitemapSpider, self).__init__(*args, **kwargs)

        self.start_url = self.sitemap_urls[0]

        # offline = True
        # # 'file:///path/to/file.html'
        # self.start_url = self.sitemap_urls[0] if not offline else 'file:///' + abs_data_dir + '.html'

        self.stock = stock_info['symbol']
        self.abs_data_dir = abs_data_dir[stock_info['symbol']]

    # method for restricting sites by date
    # also this should restrict the pages to be crawled
    # def sitemap_filter(self, entries):
    #     for entry in entries:
    #         yield entry
    # date_time = datetime.strptime(entry['lastmod'], '%Y-%m-%d')
    # if date_time.year >= 2005:
    #     yield entry

    # def parse_offline(self, response):
    #     # sitemap = etree.fromstring(response)
    #     # file:///path/to/file.html

        

    # TODO: failing to pass the response to save it as an html file for preprocesing it later
    def parse(self, response):
        # sitemap = etree.fromstring(response)
        # file:///path/to/file.html

        yield {
            'url': response.url,
            'body': response.body,
            'url_referer': response.request.headers.get('Referer', None).decode('utf-8')
        }
        # yield HtmlItem(url=response.url, body=response.body, url_referer=response.request.headers.get('Referer', None))
