import argparse
import json
from os import listdir
from os.path import isfile, join


class SizeDoesNotMatchException(Exception):
    pass


def compare_size(s1, s2):
    if len(s1) != len(s2):
        raise SizeDoesNotMatchException("data size does not match")


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", default="movies_search_count", help="path of the json directory", type=str)
parser.add_argument("-j", "--jsonfile", default="search_count.json", help="path of the search_count.json", type=str)
args = parser.parse_args()

extension = '.json'
key = 'search_count'
files = [int(f.rstrip(extension)) for f in listdir(args.directory) if isfile(join(args.directory, f))]
files.sort()

files = [args.directory + '/' + str(f) + extension for f in files]

with open(args.jsonfile, 'r') as jsonfile:
    search_count = json.loads(jsonfile.read())


try:
    compare_size(files, search_count)
    for file, sc in zip(files, search_count):
        with open(file) as f:
            jf = json.loads(f.read())
            jf[key] = int(sc[key].replace(',', ''))
        with open(file, 'w') as wf:
            data = json.dump(jf, wf, ensure_ascii=False, indent=4, separators=(',', ':'))
            wf.write("\n")


except SizeDoesNotMatchException as e:
    print("size", len(files), "does not match size", len(search_count))
    print("Exception: ", e)
