import argparse
import json
import re

import requests
from lxml import html


class DumpOtherNominate:

    # Dump the prize winners of each award.

    def __init__(self, output, since, until):
        self._output = output
        self._since = since
        self._until = until

    @property
    def output(self):
        return self._output

    @property
    def since(self):
        return self._since

    @property
    def until(self):
        return self._until

    def years(self):
        yield from range(self.since, self.until)

    def run(self):
        award_data = [
            self.register_nikkan_sports(),
            self.register_golden_gross(),
            self.register_hochi_eigashou(),
            self.register_mainichi_film_award(),
            self.register_blue_ribbon_award(),
            self.kinejun_best_ten(),
        ]

        results = []
        for year in self.years():
            result = {'year': year, 'prize_winners': []}
            for data in award_data:
                info = {'award': data[0]}

                year_data = list(self._filter_by_year(data[1], year))
                if not year_data:
                    continue

                title = self._convert_to_half_width(year_data[0]['title'])
                info['work'] = {'index': -1, 'title': title}
                result['prize_winners'].append(info)
            results.append(result)

        with open(self.output, 'w') as output:
            json.dump(results, output,
                      ensure_ascii=False,
                      indent=4,
                      separators=(',', ':'))
            output.write('\n')

    def _filter_by_year(self, lst, year):
        for elm in lst:
            if elm['year'] == year:
                yield elm

    def create_map(self, whole_data):
        data = []
        for year in self.years():
            for caption, title in whole_data.items():
                data_map = {}
                if str(year) in caption:
                    data_map['year'] = year
                    data_map['title'] = title
                    data.append(data_map)
                    break
        return data

    def register_nikkan_sports(self):
        url = 'https://www.nikkansports.com/entertainment/award/ns-cinema/history/'
        root = self._get_root(url)
        whole_data = {}
        for table in root.xpath('//table[contains(@class, "nsTable")]'):
            caption = table.xpath('caption')[0].text
            data = table.xpath('tr[1]/td[1]')[0].text
            if data is None:
                data = table.xpath('tr[1]/td[1]/a')[0].text
            whole_data[caption] = data
        return 'nikkan_sports', self.create_map(whole_data)

    def register_golden_gross(self):
        url = 'https://ja.wikipedia.org/wiki/ゴールデングロス賞'
        root = self._get_root(url)
        whole_data = {}

        for row in root.xpath('//table[contains(@class, "wikitable")]/tbody/tr'):
            if not row.xpath('td[1]/a'):
                continue

            if not row.xpath('td[3]/a'):
                continue

            caption = row.xpath('td[1]/a')[0].text
            data = row.xpath('td[3]/a')[0].text
            whole_data[caption] = data

        return 'golden_gross', self.create_map(whole_data)

    def register_hochi_eigashou(self):
        url = 'https://www.hochi.co.jp/award/hochi_eigashou/history.html'
        root = self._get_root(url)
        whole_data = {}

        for row in root.xpath('//table[contains(@class, "btable")]/tr'):
            if not row.xpath('td[2]'):
                continue

            if not row.xpath('td[3]'):
                continue

            caption = row.xpath('td[2]')[0].text
            data = row.xpath('td[3]')[0].text
            whole_data[caption] = data

        whole_data['2018年'] = '孤狼の血'    # has not yet been uploaded
        return 'hochi_eigashou', self.create_map(whole_data)

    def register_mainichi_film_award(self):
        url = 'https://mainichi.jp/mfa/history/'
        root = self._get_root(url)
        whole_data = {}
        for row in root.xpath('//ul[contains(@class, "list-history")]/li'):
            text = row.xpath('a')[0].text
            caption = text[:4]
            data = re.search('(?<=『).*?(?=』)', text).group(0)
            whole_data[caption] = data
        return 'mainichi_film_award', self.create_map(whole_data)

    def register_blue_ribbon_award(self):
        url = 'https://mihocinema.com/blueribbon-list'
        root = self._get_root(url)
        whole_data = {}

        for row in root.xpath('//table//tr'):
            if not row.xpath('td'):
                continue

            year = row.xpath('td[2]/text()')[0]

            if row.xpath('td[3]/text()'):
                data = row.xpath('td[3]/text()')[0]
            else:
                data = row.xpath('td[3]/a/text()')[0]

            whole_data[year] = data

        return 'blue_ribbon_award', self.create_map(whole_data)

    def kinejun_best_ten(self):
        url = 'http://www.kinenote.com/main/award/kinejun/'
        root = self._get_root(url)
        whole_data = {}

        for row in root.xpath('//table[contains(@class, "tbl_year")]/tr'):
            if not row.xpath('td[1]/a'):
                continue

            if not row.xpath('td[3]/a'):
                continue

            caption = row.xpath('td[1]/a')[0].text
            data = row.xpath('td[3]/a')[0].text
            whole_data[caption] = data

        whole_data['2018年'] = '万引き家族'  # has not yet been uploaded
        return 'kinejun_best_ten', self.create_map(whole_data)

    @staticmethod
    def _get_root(url):
        page = requests.get(url)
        root = html.fromstring(page.content)
        return root

    @staticmethod
    def _convert_to_half_width(fullwidth):
        table = {chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}
        trans = str.maketrans(table)
        text = fullwidth.translate(trans)
        return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output",
                        default="annual_other_nominate_data.json",
                        help="path of the output json file",
                        type=str)
    parser.add_argument("--since", default=1978, help="since", type=int)
    parser.add_argument("--until", default=2020, help="until", type=int)
    args = parser.parse_args()

    dump_other_nominate = DumpOtherNominate(args.output,
                                            args.since,
                                            args.until)

    dump_other_nominate.run()
