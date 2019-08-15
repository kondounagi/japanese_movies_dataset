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
        self.output = []
        self.years = range(2003, 2019)

    def __call__(self, *args, **kwargs):
        self.files = self.create_files_list()
        self.modify_index()
        self.dump_data()

    def create_files_list(self):
        extension = '.json'
        files = [int(f.rstrip(extension)) for f in listdir(self.args.directory)
                 if isfile(join(self.args.directory, f))]
        files.sort()
        return [self.args.directory + '/' + str(f) + extension for f in files]

    def _filter_by_year(self, lst, year):
        for elm in lst:
            if elm['year'] == year:
                yield elm

    def modify_index(self):
        with open(self.args.jsonfile, 'r') as jsonfile:
            other_nominate = json.loads(jsonfile.read())

        # OPTIMIZE:	this nests too deep ...
        for year in self.years:
            current = list(self._filter_by_year(other_nominate, year))
            if not current:
                continue

            add_data = current[0]

            movielist = '../{}_movie_clean'.format(year)
            year_data = []

            for prize in add_data['prize_winners']:
                with open(movielist) as f:
                    for movie in f:
                        index, title = movie.split('\t')[0:2]
                        index = int(index)

                        if title == prize['work']['title']:
                            add_prize = prize
                            add_prize['work']['index'] = index
                            year_data.append(add_prize)
                            break
                    else:
                        year_data.append(prize)

            add_data['prize_winners'] = year_data
            self.output.append(add_data)

        with open(self.args.jsonfile, 'w') as jsonfile:
            json.dump(self.output, jsonfile,
                      ensure_ascii=False,
                      indent=4,
                      separators=(',', ':'))
            jsonfile.write('\n')

    def dump_data(self):
        for year in self.years:
            movielist = '../{}_movie_clean'.format(year)
            with open(movielist) as f:
                for movie in f:
                    nominates = []
                    index, title = movie.split('\t')[0:2]
                    index = int(index)

                    file_name = ('movies_other_nominate/{year}/{index}.json'
                                 .format(year=year, index=index))

                    for award in self.output:
                        if year == award['year']:
                            for winner in award['prize_winners']:
                                result = {}
                                i = winner['work']['index']
                                if index == i:
                                    nominates.append({
                                        'nominate_name': winner['award'],
                                    })
                                result['title'] = title
                                result['other_nominate'] = nominates

                    with open(file_name, 'w') as wf:
                        json.dump(result, wf,
                                  ensure_ascii=False,
                                  indent=4,
                                  separators=(',', ':'))
                        wf.write('\n')


def main():
    register_other_nominate = RegisterOtherNominate()
    register_other_nominate()


if __name__ == '__main__':
    main()
