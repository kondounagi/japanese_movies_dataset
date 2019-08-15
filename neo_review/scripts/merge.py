import json
import os
import sys


def main(meta_filepath, input_dir, output_filepath):
    meta_data = None
    with open(meta_filepath, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)

    output_dict = {}

    for year in meta_data.keys():
        for element in meta_data[year]:
            nomination_id = element['id']
            with open(input_dir.rstrip('/') + '/{}.json'.format(nomination_id), 'r', encoding='utf-8') as f:
                data = json.load(f)
                output_dict.update(data)

    with open(output_filepath, 'w', encoding='utf-8') as output:
        json.dump(output_dict, output, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4:
        print('disignate filepath')
        sys.exit(0)
    if len(args) == 4:
        main(args[1], args[2], args[3])
