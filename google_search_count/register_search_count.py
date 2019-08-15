import argparse
import glob
import json
import os
import re


class SizeDoesNotMatchException(Exception):
    pass


def compare_size(s1, s2):
    if len(s1) != len(s2):
        raise SizeDoesNotMatchException("data size does not match")


parser = argparse.ArgumentParser()

parser.add_argument("-d", "--directory",
                    default="movies_search_count",
                    help="path of the json directory",
                    type=str)

parser.add_argument("-j", "--jsonfile",
                    default="search_count.json",
                    help="path of the search_count.json",
                    type=str)

args = parser.parse_args()

key = 'search_count'
files = glob.glob(os.path.join(glob.escape(args.directory), '*.json'))
files.sort(key=lambda p: int(re.findall(r'\d+', p)[-1]))

with open(args.jsonfile, 'r') as jsonfile:
    search_count = json.loads(jsonfile.read())


try:
    compare_size(files, search_count)
    for path, sc in zip(files, search_count):
        with open(path) as f:
            jf = json.loads(f.read())
            jf[key] = int(sc[key].replace(',', ''))
        with open(path, 'w') as wf:
            data = json.dump(jf, wf,
                             ensure_ascii=False,
                             indent=4,
                             separators=(',', ':'))
            wf.write("\n")


except SizeDoesNotMatchException as e:
    print("size", len(files), "does not match size", len(search_count))
    print("Exception: ", e)
