import glob
import os
import csv
import json


def generate_wsj_csv(abs_data_dir):
    all_files = glob.glob(abs_data_dir + "*.jl")

    for jl_file in all_files:
        filename = os.path.basename(jl_file).split('.jl')[0]  # getting only filename without extension and path

        with open(abs_data_dir + filename + '.csv', "w") as csv_file, open(jl_file, "r") as input_file:
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
                                [doc_id, creation_date, 'Bitcoin', headline, sub_headline, abstract])
