import argparse
import json
import re

import requests
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class DumpOtherNominate:

    # Dump the prize winners of each award.

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

        parser = argparse.ArgumentParser()
        parser.add_argument("-o", "--output",
                            default="annual_other_nominate_data.json",
                            help="path of the output json file",
                            type=str)
        self.args = parser.parse_args()

        self.years = range(2003, 2019)

    def __call__(self, *args, **kwargs):
        award_data = [self.register_nikkan_sports(), self.register_golden_gross(), self.register_hochi_eigashou(),
                      self.register_mainichi_film_award(), self.register_blue_ribbon_award(), self.kinejun_best_ten()]
        results = []
        for year in self.years:
            result = {'year': year, 'prize_winners': []}
            for data in award_data:
                info = {'award': data[0]}
                if len([x for x in data[1] if x['year'] == year]) == 0:
                    continue
                title = convert_to_half_width([x for x in data[1] if x['year'] == year][0]['title'])
                info['work'] = {'index': -1, 'title': title}
                result['prize_winners'].append(info)
            results.append(result)

        with open(self.args.output, 'w') as output:
            json.dump(results, output, ensure_ascii=False, indent=4, separators=(',', ':'))
            output.write('\n')

    def create_map(self, whole_data):
        data = []
        for year in self.years:
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
        root = get_root(url)
        whole_data = {}
        for table in root.xpath('//table[contains(@class, "nsTable")]'):
            caption = table.xpath('caption')[0].text
            data = table.xpath('tr[1]/td[1]')[0].text
            if data is None:
                data = table.xpath('tr[1]/td[1]/a')[0].text
            whole_data[caption] = data
        return 'nikkan_sports', self.create_map(whole_data)

    def register_golden_gross(self):
        url = 'https://ja.wikipedia.org/wiki/%E3%82%B4%E3%83%BC%E3%83%AB%E3%83%87%E3%83%B3%E3%82%B0%E3%83%AD%E3%82%B9' \
              '%E8%B3%9E'
        root = get_root(url)
        whole_data = {}
        for row in root.xpath('//table[contains(@class, "wikitable")]/tbody/tr'):
            if len(row.xpath('td[1]/a')) == 0 or len(row.xpath('td[3]/a')) == 0:
                continue
            caption = row.xpath('td[1]/a')[0].text
            data = row.xpath('td[3]/a')[0].text
            whole_data[caption] = data
        return 'golden_gross', self.create_map(whole_data)

    def register_hochi_eigashou(self):
        url = 'https://www.hochi.co.jp/award/hochi_eigashou/history.html'
        root = get_root(url)
        whole_data = {}
        for row in root.xpath('//table[contains(@class, "btable")]/tr'):
            if len(row.xpath('td[2]')) == 0 or len(row.xpath('td[3]')) == 0:
                continue
            caption = row.xpath('td[2]')[0].text
            data = row.xpath('td[3]')[0].text
            whole_data[caption] = data
        whole_data['2018年'] = '孤狼の血'    # has not yet been uploaded
        return 'hochi_eigashou', self.create_map(whole_data)

    def register_mainichi_film_award(self):
        url = 'https://mainichi.jp/mfa/history/'
        root = get_root(url)
        whole_data = {}
        for row in root.xpath('//ul[contains(@class, "list-history")]/li'):
            text = row.xpath('a')[0].text
            caption = text[:4]
            data = re.search('(?<=『).*?(?=』)', text).group(0)
            whole_data[caption] = data
        return 'mainichi_film_award', self.create_map(whole_data)

    def register_blue_ribbon_award(self):
        url = 'http://www.allcinema.net/prog/award_top.php?num_a=41'
        root = get_root(url)
        whole_data = {}
        for row in root.xpath('//tr[contains(@class, "c2")]'):
            fullwidth = row.xpath('td[1]/a')[0].text
            caption = convert_to_half_width(fullwidth)
            data = row.xpath('td[3]/a')[0].text.replace('\u3000', ' ')
            whole_data[caption] = data
        return 'blue_ribbon_award', self.create_map(whole_data)

    def kinejun_best_ten(self):
        url = 'http://www.kinenote.com/main/award/kinejun/'
        root = get_root(url)
        whole_data = {}
        for row in root.xpath('//table[contains(@class, "tbl_year")]/tr'):
            if len(row.xpath('td[1]/a')) == 0 or len(row.xpath('td[3]/a')) == 0:
                continue
            caption = row.xpath('td[1]/a')[0].text
            data = row.xpath('td[3]/a')[0].text
            whole_data[caption] = data
        whole_data['2018年'] = '万引き家族'  # has not yet been uploaded
        return 'kinejun_best_ten', self.create_map(whole_data)


def get_root(url):
    page = requests.get(url)
    root = html.fromstring(page.content)
    return root


def convert_to_half_width(fullwidth):
    text = fullwidth.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))
    return text


def main():
    dump_other_nominate = DumpOtherNominate()
    dump_other_nominate()


if __name__ == '__main__':
    main()
