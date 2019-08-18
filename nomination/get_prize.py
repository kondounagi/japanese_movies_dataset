import certifi
import urllib3
from bs4 import BeautifulSoup
import json


def main():
    for n_th in range(1, 42 + 1):
        data = get_prize(n_th)
        with open('./{}.json'.format(str(n_th + 1976)), 'w') as output:
            json.dump(data, output, indent=4, ensure_ascii=False)
            output.write('\n')


def get_prize(n_th):
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                               ca_certs=certifi.where())

    url = 'https://www.japan-academy-prize.jp/prizes/'
    r = http.request('GET', url, fields={'t': n_th})
    data = r.data.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')

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

    prize_dict = {'n_th': n_th}

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
        prize_dict[prize]['最優秀賞'] = anker.findNext('img', {'alt': '最優秀賞'}).nextSibling.string
        elements = anker.findAllNext('img', {'alt': '優秀賞'})
        filtered = []
        for element in elements:
            if element.findPrevious('div', {'class': 'subtitle'}).find('img')['alt'] != prize:
                break
            filtered.append(element)
        prize_dict[prize]['優秀賞'] = [element.nextSibling.string for element in filtered]

    return prize_dict


if __name__ == '__main__':
    main()
