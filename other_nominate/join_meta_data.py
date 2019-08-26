import argparse
import json


class JoinMetaData:

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-o",
            "--original",
            default="../neo_review/data/nominate_movie_meta_data.json",
            help="path of the original json file",
            type=str,
        )

        parser.add_argument(
            "-d",
            "--data",
            default="meta_movie_data/nominate_movie_meta_data.json",
            help="path of the target json file",
            type=str,
        )

        parser.add_argument(
            "-s",
            "--summary",
            default="annual_other_nominate_data.json",
            help="path of the other nominate list json",
            type=str,
        )

        self.args = parser.parse_args()

        self.years = range(1978, 2020)

    def __call__(self, *args, **kwargs):
        nominate_map = self.create_map()
        self.read_original(nominate_map)

    def create_map(self):
        results = {}
        with open(self.args.summary, 'r') as f:
            summary = json.load(f)
        for annual_data in summary:
            for data in annual_data['prize_winners']:
                if data['work']['title'] not in results.keys():
                    results[data['work']['title']] = []
                results[data['work']['title']].append({'award': data['award']})
        return results

    def read_original(self, nominate_map):
        with open(self.args.original, 'r') as f:
            original = json.load(f)

        # Initialize dataset
        other_nominates = [{'award': n, 'prized': 0} for n in [
            'nikkan_sports',
            'golden_gross',
            'hochi_eigashou',
            'mainichi_film_award',
            'blue_ribbon_award',
            'kinejun_best_ten',
        ]]

        result = {}
        for year in self.years:
            result[str(year)] = []
            for movie_data in original[str(year)]:
                # print("#", movie_data)
                movie_data['other_nominates'] = other_nominates
                if movie_data['title'] in nominate_map:
                    movie_data['other_nominates'] = []
                    for nominate in other_nominates:
                        for element in nominate_map[movie_data['title']]:
                            if nominate['award'] == element['award']:
                                movie_data['other_nominates'].append({
                                    'award': nominate['award'],
                                    'prized': 1,
                                })

                                break
                        else:
                            movie_data['other_nominates'].append({
                                'award': nominate['award'],
                                'prized': 0,
                            })

                result[str(year)].append(movie_data)

        with open(self.args.data, 'w') as f:
            json.dump(result, f,
                      ensure_ascii=False,
                      indent=4,
                      separators=(',', ':'))
            f.write('\n')


def main():
    join_meta_data = JoinMetaData()
    join_meta_data()


if __name__ == '__main__':
    main()
