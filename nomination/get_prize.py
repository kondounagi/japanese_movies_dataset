import certifi
import re
import urllib
import urllib3
from bs4 import BeautifulSoup
import json

BASE_YEAR = 1976


def main():
    for year, url in prize_list():
        data = get_prize(url)
        with open('./{}.json'.format(str(year)), 'w') as output:
            json.dump(data, output, indent=4, ensure_ascii=False)
            output.write('\n')


def http_get(url, fields=None):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    req = http.request('GET', url, fields=fields)
    data = req.data.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')

    return soup


def prize_list():
    url = 'https://www.japan-academy-prize.jp/prizes/view.php'
    soup = http_get(url)

    for elm in soup.select('.main .one'):
        nth = elm.select_one('.kai').get_text()
        rel = elm.select_one('.btn a')["href"]

        match = re.match(r'第(\d+)回', nth)
        if not match:
            continue

        yield (
            BASE_YEAR + int(match.group(1)),
            urllib.parse.urljoin(url, rel),
        )


def get_prize(url):
    soup = http_get(url)

    prize_list1 = [
        '優秀作品賞',
        '優秀アニメーション作品賞',
    ]

    prize_list2 = [
        '優秀監督賞',
        '優秀脚本賞',
        '優秀主演男優賞',
        '優秀主演女優賞',
        '優秀助演男優賞',
        '優秀助演女優賞',
        '優秀音楽賞',
        '優秀撮影賞',
        '優秀照明賞',
        '優秀美術賞',
        '優秀録音賞',
        '優秀編集賞',
        '優秀外国作品賞',
    ]

    prize_dict = {}

    for prize in prize_list1 + prize_list2:
        prize_dict[prize] = {'最優秀賞': None, '優秀賞': None}

    for prize in prize_list1:
        ref = soup.find('img', {'alt': prize})
        if ref:
            anker = ref.findParent('div', {'class': 'subtitle'})

        if anker is None:
            continue
        elements = anker.findNext('ul').findAll('li')

        titles = []
        for element in elements:
            div = element.select_one('div.text01')
            if div:
                titles.append(div.string)

        prize_dict[prize]['最優秀賞'] = titles[0]
        prize_dict[prize]['優秀賞'] = titles[1:]

    for prize in prize_list2:
        ref = soup.find('img', {'alt': prize})
        if ref:
            anker = ref.findParent('div', {'class': 'subtitle'})

        if anker is None:
            continue

        prize_dict[prize]['最優秀賞'] = (anker
                                     .findNext('img', {'alt': '最優秀賞'})
                                     .nextSibling.string)

        elements = anker.findAllNext('img', {'alt': '優秀賞'})
        filtered = []

        for element in elements:
            subtitle_alt = (element
                            .findPrevious('div', {'class': 'subtitle'})
                            .find('img')['alt'])

            if subtitle_alt != prize:
                break

            filtered.append(element)

        prize_dict[prize]['優秀賞'] = (
            [element.nextSibling.string for element in filtered])

    return prize_dict


if __name__ == '__main__':
    main()
