import glob
import os
import csv
import json
import pandas as pd

SYMBOLS_DICT = {
    'btcusd': 'Bitcoin',
    'appl': 'Apple'
}


def remove_duplicates(filename):
    in_file = glob.glob(filename)[0]

    df = pd.read_csv(in_file, index_col=None, header=0, sep=';')

    df.drop_duplicates(subset=['doc_id'], inplace=True)

    df.to_csv(filename, sep=';', encoding='utf-8', index=False)


def generate_wsj_csv(abs_data_dir, stock='btcusd'):
    all_files = glob.glob(abs_data_dir + "*.jl")

    for jl_file in all_files:
        filename = os.path.basename(jl_file).split('.jl')[0]  # getting only filename without extension and path
        complete_fpath = abs_data_dir + filename + '.csv'

        with open(complete_fpath, "w") as csv_file, open(jl_file, "r") as input_file:
            csv_writter = csv.writer(csv_file, delimiter=';')
            csv_writter.writerow(
                ['doc_id', 'datetime', 'company', 'title', 'sub_headline', 'abstract'])

            for line in input_file:
                json_res = json.loads(line.strip())

                csv_writter = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)

                for json_list in json_res['HeadlinesResponse']:
                    # the sumamry object is one to check to see if there is any
                    # more response beyond a given date
                    if json_list['Summary']:
                        for item in json_list['Summary']:
                            doc_id = int(item['DocumentIdUri'].split('/')[-1])
                            creation_date = item['CreateTimestamp']['Value']
                            headline = item['Headline']
                            # body_headline = item['BodyHeadline'] # for some reason the headline appears twice in the json, with different keys, not sure if they can differ sometimes
                            sub_headline = item.get("SubHeadline", None)
                            abstract = item['Abstract']['ABSTRACT']['#text'] if 'Abstract' in item else None

                            csv_writter.writerow(
                                [doc_id, creation_date, SYMBOLS_DICT[stock], headline, sub_headline, abstract])

        remove_duplicates(complete_fpath)
