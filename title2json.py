#!/usr/bin/env python3
import csv
import json


def main():
    with open("2018_movie_clean", 'r') as src:
        for num, name, *_ in csv.reader(src, delimiter='\t'):
            with open("movies/{}.json".format(num), 'r+') as f:
                data = json.load(f)
                data['title'] = name
                f.seek(0)
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
                f.truncate()


if __name__ == '__main__':
    main()
