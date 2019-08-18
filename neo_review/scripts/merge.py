import json
import os
import sys


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def store_json(filepath, obj):
    with open(filepath, 'w') as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)
        f.write('\n')


def main(meta_filepath, input_dir, output_filepath):
    meta_data = load_json(meta_filepath)

    output_dict = {}

    for year in meta_data.keys():
        for element in meta_data[year]:
            nomination_id = element['id']

            json_path = os.path.join(input_dir,
                                     '{}.json'.format(nomination_id))

            data = load_json(json_path)
            output_dict.update(data)

    store_json(output_filepath, output_dict)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4:
        print('disignate filepath')
        sys.exit(0)
    if len(args) == 4:
        main(args[1], args[2], args[3])
