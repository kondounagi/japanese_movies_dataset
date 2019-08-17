#!/usr/bin/env python3
import certifi
import urllib3
import urllib
from bs4 import BeautifulSoup
import re
import csv
import sys
import json
import os


def uncommify(text):
    return int(text.replace(',', ''))


def main(filepath: str, output_dir: str, start_row=1, end_row=None):
    titles = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            title = row[1]
            titles.append(title)

    if end_row is not None:
        if end_row > len(titles):
            end_row = len(titles)
    else:
        end_row = len(titles)

    for i in range(start_row - 1, end_row):
        title = titles[i]
        select = get_coco_id(title)
        comments = get_coco_review(select)
        data = get_coco_data(select)
        comment_dict = {
            'title': title,
            'id': i,
            'data': {'eigacom': [], 'filmarks': [], 'coco': data},
            'reviews': {'eigacom': [], 'filmarks': [], 'coco': comments},
        }

        os.makedirs(output_dir, exist_ok=True)
        output_file = output_dir.rstrip('/') + '/{}.json'.format(str(i + 1))
        with open(output_file, 'w') as output:
            json.dump(comment_dict, output, indent=4, ensure_ascii=False)
            output.write('\n')

    return


def get_coco_id(title):
    def trans(title_string):
        table = str.maketrans({
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
            '０': '0',
            '＆': '&',
            '％': '%',
            '＝': '=',
            '＄': '$',
            '＃': '#',
            '！': '!',
            '？': '?',
        })
        regulated_title = re.sub(r'（[^（）]*）', '', title_string)
        regulated_title = re.sub(r'\([^\(\)]*\)', '', regulated_title)

        regulated_title = re.sub(r'''
            [\s\-～〜:：;、。<>＜＞「」\"\',\.・/／－]+  # unwanted signs
        ''', ' ', regulated_title, flags=re.VERBOSE)

        regulated_title = regulated_title.translate(table)
        regulated_title = regulated_title.rstrip(' ')
        return regulated_title

    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    url = 'https://coco.to/movies'

    regulated_title = trans(title)

    req = http.request('GET', url, fields={'q': regulated_title})
    data = req.data.decode('utf-8')

    soup = BeautifulSoup(data, 'html.parser')

    id_title = []
    for element in soup.select("div.li_pp"):
        temp_id = re.sub(r'\D', '', element.a['href'])
        temp_title = element.select_one('div.li_ttl').string
        id_title.append({'cocoId': temp_id, 'title': temp_title})

    for element in id_title:
        temp_title = element['title']
        temp_title = trans(temp_title)
        temp_title = temp_title.replace('...', '')
        element['title'] = temp_title

    regulated_title = trans(title)
    regulated_title = regulated_title.replace('...', '')

    select = None

    for element in id_title:
        min_length = min(len(element['title']), len(regulated_title))
        if regulated_title[:min_length] == element['title'][:min_length]:
            select = element
            break

    if select is None and len(id_title) != 0:
        select = id_title[0]

    return select


def get_coco_review(select):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    comments = []
    if select is None:
        return comments

    for i in range(200):
        url = ('https://coco.to/movie/{}/review/{}'
               .format(select['cocoId'], str(i + 1)))

        encoded_url = urllib.parse.quote(url, '/:?=&')
        req = http.request('GET', encoded_url)
        data = req.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        flag = False

        if len(soup.select('h2.tweet_title2')) > 0:
            flag = True

        if len(soup.select('h2.tweet_title1')) > 0:
            flag = True

            li = soup.select('li.tweet_li')

        if len(li) == 0:
            flag = True

        for counter, each in enumerate(li):
            comment_string = each.select_one('div.tweet_text').next_element
            processed_comment = re.sub(r'\s', ' ', comment_string)
            comments.append(processed_comment)

        if flag:
            break

    return(comments)


def get_coco_data(select):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    url = 'https://coco.to/movies'

    data_dict = {
        'satisfaction': None,
        'whole_tweet_amount': None,
        'each_tweet_amount': {
            'good': None,
            'even': None,
            'bad': None,
        },
        'positive_index': None,
        'review_word': [],
    }

    if select is not None:
        return data_dict

    url = 'https://coco.to/movie/{}'.format(select['cocoId'])
    encoded_url = urllib.parse.quote(url, '/:?=&')
    req = http.request('GET', encoded_url)
    data = req.data.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')

    satisfaction_element = (
        soup.find('span', {'style': 'font-size:45px;margin-right:5px'}))
    if satisfaction_element:
        data_dict['satisfaction'] = (
            uncommify(satisfaction_element.string))

    review_good_element = soup.select_one('div.review_good').nextSibling
    if review_good_element:
        data_dict['each_tweet_amount']['good'] = (
            uncommify(review_good_element.string))

    review_even_element = soup.select_one('div.review_even').nextSibling
    if review_even_element:
        data_dict['each_tweet_amount']['even'] = (
            uncommify(review_even_element.string))

    review_bad_element = soup.select_one('div.review_bad').nextSibling
    if review_bad_element:
        data_dict['each_tweet_amount']['bad'] = (
            uncommify(review_bad_element.string))

    tweet_amount_element = (
        soup.find('span', {'style': 'font-size:17px;margin-right:2px'}))
    if tweet_amount_element:
        data_dict['whole_tweet_amount'] = (
            uncommify(tweet_amount_element.string))

    positive_index_element = (
        soup.find('span', {'style': 'font-size:15px;margin:0 2px 0 3px'}))
    if positive_index_element:
        data_dict['positive_index'] = (
            uncommify(positive_index_element.string))

    review_keyword_wrapper = soup.select_one('div.tag_list.clearflt.clearboth')
    if review_keyword_wrapper:
        review_keyword_elements = review_keyword_wrapper.findAll('a')

    for element in review_keyword_elements:
        keyword_dict = {'keyword': None, 'grade': None}
        keyword_dict['keyword'] = element.string
        match = re.search(r'font\-size:\d+px', element['style'])
        font_size_style = match.group()
        size = re.sub(r'\D', '', font_size_style)
        mapping = {
            '10': '少し',
            '11': '少し',
            '12': '少し',
            '13': 'まあまあ多い',
            '14': 'まあまあ多い',
            '15': 'まあまあ多い',
            '16': 'まあまあ多い',
            '17': '結構多い',
            '18': '結構多い',
            '19': '結構多い',
            '20': '結構多い',
            '21': 'とても多い',
            '22': 'とても多い',
            '23': 'とても多い',
            '24': 'とても多い',
        }
        keyword_dict['grade'] = mapping.get(size, '不明')
        data_dict['review_word'].append(keyword_dict)

    return data_dict


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 3:
        print('disignate filepath')
        sys.exit(0)
    if len(args) == 3:
        main(args[1], args[2])
    if len(args) == 4:
        main(args[1], args[2], start_row=int(args[3]))
    if len(args) == 5:
        main(args[1], args[2], start_row=int(args[3]), end_row=int(args[4]))
