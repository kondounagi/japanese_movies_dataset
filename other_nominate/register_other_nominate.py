import argparse
import json
from os import listdir
from os.path import isfile, join


class RegisterOtherNominate:

    # Register the prize winners of each award to the formatting style.

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--directory",
                            default="movies_other_nominate",
                            help="path of the json directory",
                            type=str)
        parser.add_argument("-j", "--jsonfile",
                            default="annual_other_nominate_data.json",
                            help="path of the other nominate json data",
                            type=str)
        self.args = parser.parse_args()

        self.key = 'other_nominate'
        self.years = range(2003, 2019)

    def __call__(self, *args, **kwargs):
        self.files = self.create_files_list()
        self.modify_index()

    def create_files_list(self):
        extension = '.json'
        files = [int(f.rstrip(extension)) for f in listdir(self.args.directory)
                 if isfile(join(self.args.directory, f))]
        files.sort()
        return [self.args.directory + '/' + str(f) + extension for f in files]

    def modify_index(self):
        with open(self.args.jsonfile, 'r') as jsonfile:
            other_nominate = json.loads(jsonfile.read())

        output = []
        # OPTIMIZE:	this nests too deep ...
        for year in self.years:
            data = [d for d in other_nominate if d['year'] == year][0]
            movielist = '../{}_movie_clean'.format(year)
            add_data = data
            year_data = []
            if year == data['year']:
                for prize in data['prize_winners']:
                    with open(movielist) as f:
                        for movie in f:
                            index, title = movie.split('\t')[0], movie.split('\t')[1]
                            if title == prize['work']['title']:
                                add_prize = prize
                                add_prize['work']['index'] = int(index)
                                year_data.append(add_prize)
                                break
                        else:
                            year_data.append(prize)

                add_data['prize_winners'] = year_data
                output.append(add_data)

        with open(self.args.jsonfile, 'w') as jsonfile:
            json.dump(output, jsonfile, ensure_ascii=False, indent=4, separators=(',', ':'))


def main():
    register_other_nominate = RegisterOtherNominate()
    register_other_nominate()


if __name__ == '__main__':
    main()
