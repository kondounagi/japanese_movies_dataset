import argparse
import json
from os import listdir


class JoinMetaData:

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--original",
                            default="../meta_movie_data",
                            help="path of the directory with original json files",
                            type=str)
        parser.add_argument("-d", "--data",
                            default="meta_movie_data",
                            help="path of the target directory",
                            type=str)
        parser.add_argument("-s", "--summary",
                            default="annual_other_nominate_data.json",
                            help="path of the other nominate list json",
                            type=str)
        self.args = parser.parse_args()

        self.years = range(2010, 2019)

    def __call__(self, *args, **kwargs):
        nominate_map = self.create_map()
        self.read_original(nominate_map)

    def create_map(self):
        results = {}
        with open(self.args.summary, 'r') as f:
            summary = json.loads(f.read())
        for annual_data in summary:
            for data in annual_data['prize_winners']:
                if data['work']['title'] not in results.keys():
                    results[data['work']['title']] = []
                results[data['work']['title']].append({'award': data['award']})
        return results

    def read_original(self, nominate_map):
        for year in self.years:
            for file in listdir('{directory}/{year}'.format(directory=self.args.original,
                                                            year=year)):
                file_name = '{directory}/{year}/{name}'.format(directory=self.args.original,
                                                               year=year,
                                                               name=file)
                with open(file_name, 'r') as f:
                    original = json.loads(f.read())
                    other_nominates = [
                        {
                            'award': 'nikkan_sports',
                            'prized': 0
                        },
                        {
                            'award': 'golden_gross',
                            'prized': 0
                        },
                        {
                            'award': 'hochi_eigashou',
                            'prized': 0
                        },
                        {
                            'award': 'mainichi_film_award',
                            'prized': 0
                        },
                        {
                            'award': 'blue_ribbon_award',
                            'prized': 0
                        },
                        {
                            'award': 'kinejun_best_ten',
                            'prized': 0
                        }
                    ]
                    data = []
                    if original['title'] in nominate_map:
                        for nominate in other_nominates:
                            for element in nominate_map[original['title']]:
                                if nominate['award'] == element['award']:
                                    data.append({'award': nominate['award'], 'prized': 1})
                                    break
                            else:
                                data.append({'award': nominate['award'], 'prized': 0})
                        other_nominates = data

                    original['other_nominate'] = other_nominates
                output_file = '{directory}/{year}/{name}'.format(directory=self.args.data,
                                                                 year=year,
                                                                 name=file)
                with open(output_file, 'w') as f:
                    json.dump(original, f, ensure_ascii=False, indent=4, separators=(',', ':'))
                    f.write('\n')


def main():
    join_meta_data = JoinMetaData()
    join_meta_data()


if __name__ == '__main__':
    main()
