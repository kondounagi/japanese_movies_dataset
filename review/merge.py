#!/usr/bin/env python3
import json
import csv
import sys


def main(list_file_path, review_root_path):
    site_dict = {
        'eigacom': 'eigacom_review',
        'coco': 'coco_review',
    }

    with open(list_file_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            i = row[0]
            reviews = {}

            for site, path in site_dict.items():
                reviews[site] = []

                json_path = review_root_path.rstrip('/')
                json_path += '/{}/{}.json'.format(path, str(i))

                with open(json_path, 'r') as f:
                    load_data = None
                    try:
                        load_data = json.load(f)
                        reviews[site] = load_data['reviews'][site]
                    except json.decoder.JSONDecodeError:
                        reviews[site] = []

            with open('./{}.json'.format(str(i)), 'w') as output:
                json.dump({'id': i, 'reviews': reviews},
                          output,
                          indent=4,
                          ensure_ascii=False)
                output.write('\n')


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 3:
        print('disignate filepath')
    else:
        main(args[1], args[2])
