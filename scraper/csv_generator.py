import glob
import os
import csv
import json
import pandas as pd
import datetime
import pytz

from scrapy.http import HtmlResponse


# scrapy.selector.Selector


# this opens csv, remove duplicates and save the csv again
def remove_duplicates(filename, column):
    in_file = glob.glob(filename)[0]

    df = pd.read_csv(in_file, index_col=None, header=0, sep=';')

    df.drop_duplicates(subset=[column], inplace=True)

    df.to_csv(filename, sep=';', encoding='utf-8', index=False)


def generate_html_csv(abs_data_dir, stock_info):
    f_path = abs_data_dir[stock_info['symbol']]

    sub_dirs = next(os.walk(f_path))[1]  # get list of sub_dirs

    # TODO: fix this naming part, it should be similar to the way we do it in the wsj_news_spider
    dest_fname = 'newsbtc_2020-05-07T21:23:13'

    complete_fpath = f_path + dest_fname + '.csv'

    with open(complete_fpath, "w") as csv_file:
        # csv_writter = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        csv_writter = csv.writer(csv_file, delimiter=';')
        csv_writter.writerow(
            ['doc_id', 'datetime', 'mod_datetime', 'src', 'company', 'title', 'sub_headline', 'categories', 'tags'])
        src = 'news_btc'

        for sub_dir in sub_dirs:
            all_files = glob.glob(f_path + sub_dir + "/*.html")
            for html_file in all_files:
                # getting only filename without extension and path
                filename = os.path.basename(html_file).split('.html')[0]

                with open(html_file, "r") as input_file:
                    # wrapping the html file back to a response for processing
                    res = HtmlResponse(url='', body=input_file.read().encode('utf-8'))

                    doc_id = int(res.xpath('//div/@data-postid').get())
                    # TODO: maybe get data from other title, because some of the titles are wrong
                    # TODO: there is one nan case, maybe use another title source for this case:
                    # 14642	165393	2018-01-08T13:19:57+00:00	Bitcoin	NaN	https://youtu.be/bAxe9vbHn3Y	NaN	newsbtc	NaN	['uncategorized']	NaN
                    headline = res.xpath('//title/text()').get().replace('| NewsBTC', '').strip(' ')

                    published_time = res.xpath('//meta[@property="article:published_time"]/@content').get()
                    modified_time = res.xpath('//meta[@property="article:modified_time"]/@content').get()

                    sub_headline = res.xpath('//meta[@name="description"]/@content').get()

                    categs = res.xpath('//a[re:test(@class, "category-label .+")]/text()').getall()
                    categs = [x.strip().lower() for x in categs]
                    categs = list(set(categs))  # removing duplicates

                    # this part for getting the tag s and maybe other attributes is unfinished
                    # it lacks a part that after script s=extraction we use a regex to get the function that
                    # contains the dictionaries of values, xpath can only get us this far
                    # tags = res.xpath('//script[contains(., "tags")]').get() # gets the only script that we want
                    # we have to continue by string processing from now on
                    # window.newVuukleWidgets({
                    #     elementsIndex: 394519,
                    #     articleId: '394519',
                    #     img: 'https://www.newsbtc.com/wp-content/uploads/2019/08/bitcoin-buy-wall-bitmex-crypto-shutterstock_1183244413.jpg',
                    #     title: 'The Mysterious $120 Million Bitcoin Buy Wall And What it Could Mean',
                    #     tags: ', bitcoin, BitMEX, buy wall, crypto, market manipulaton, spoofing',
                    #     url: 'https://www.newsbtc.com/2019/08/28/bitcoin-buy-wall-bitmex-crypto/'
                    # });
                    # this answer may help: https://stackoverflow.com/questions/33503643/get-data-from-script-tag-in-html-using-scrapy

                    # tags = res.xpath('//script[contains(., "tags")]').get()
                    tags = []

                    csv_writter.writerow(
                        [doc_id, published_time, modified_time, src, stock_info['name'], headline, sub_headline, categs,
                         tags])

    remove_duplicates(complete_fpath, column='doc_id')


# NOTE: this code can also be useful to merge response from different runs that were not already processed to csv
def generate_wsj_csv(abs_data_dir, stock_info):
    f_path = abs_data_dir[stock_info['symbol']]
    all_files = glob.glob(f_path + "*.jl")
    est_tz = pytz.timezone('America/New_York')

    for jl_file in all_files:
        filename = stock_info['symbol'] + '_' + os.path.basename(jl_file).split('.jl')[
            0]  # getting only filename without extension and path
        complete_fpath = f_path + filename + '.csv'

        with open(complete_fpath, "w") as csv_file, open(jl_file, "r") as input_file:
            csv_writter = csv.writer(csv_file, delimiter=';')
            csv_writter.writerow(
                ['doc_id', 'datetime', 'company', 'title', 'sub_headline', 'abstract', 'ref_tickers'])

            for line in input_file:
                json_res = json.loads(line.strip())

                csv_writter = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

                for json_list in json_res['HeadlinesResponse']:
                    # the sumamry object is one to check to see if there is any
                    # more response beyond a given date
                    if json_list['Summary']:
                        for item in json_list['Summary']:
                            doc_id = int(item['DocumentIdUri'].split('/')[-1])

                            # WSJ website uses America/New_York (EST) timezone, although it does not appear in the API
                            # for the timezone ambiguity on changing instants, we found WSJ to not be reliable, and
                            # taking some time to update entries, and just for consistency, we force the time forward
                            # by setting `is_dst=True`
                            creation_date = est_tz.localize(
                                datetime.datetime.fromisoformat(item['CreateTimestamp']['Value']), is_dst=True)

                            sub_headline = item.get('SubHeadline') if item.get('SubHeadline') is None else item[
                                'SubHeadline'].replace('\n', '').strip()
                            abstract = item['Abstract']['ABSTRACT']['#text'].replace('\n',
                                                                                     '').strip() if 'Abstract' in item else None

                            # normally Headline and BodyHeadline are the same, but sometimes, headline may be empty
                            # string and so we check for empty string, and then use BodyHeadline instead
                            if item['Headline']:
                                headline = item['Headline'].replace('\n', '').strip()
                            else:
                                headline = item['BodyHeadline'].replace('\n', '').strip()

                            # TODO: doing mentioned ticker gathering, remains testing what was done,
                            #  and including information bout the mentioned category which should
                            #  be mentioned as it can be puzzling, because it is not clear what is the used
                            #  classification criteria. Also, this is becoming a big string, that may be hard to
                            #  deal with in the notebook.
                            # Example of json for using as ref:                     "Instrument": [
                            #                         {
                            #                             "Type": [
                            #                                 {
                            #                                     "Namespace": "http://service.marketwatch.com/ws/2005/09/newscloud/display",
                            #                                     "Name": "Prominent",
                            #                                     "IsEmpty": false
                            #                                 }
                            #                             ],
                            #                             "Ticker": "GOOGL",
                            #                             "Exchange": {
                            #                                 "CountryCode": "US"
                            #                             }
                            #                         },
                            ref_tickers = []
                            if 'Instrument' in item:
                                for tick in item['Instrument']:
                                    ref_tickers.append(tick['Exchange']['CountryCode'] + ':'
                                                       + tick['Ticker'])

                            csv_writter.writerow(
                                [doc_id, creation_date, stock_info['name'], headline, sub_headline, abstract,
                                 ref_tickers])

        remove_duplicates(complete_fpath, column='doc_id')
