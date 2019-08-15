#!/usr/bin/env python3
import certifi
import urllib3
import urllib
from bs4 import BeautifulSoup
import re
import sys
import json
import os


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def store_json(filepath, d):
    with open(filepath, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)
        f.write('\n')


def main(filepath: str, output_dir: str, year):
    meta_data = load_json(filepath)

    for element in meta_data[year]:
        nomination_id = element['id']
        title = element['title']
        select = get_coco_id(title)
        reviews = get_coco_review(select)

        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, '{}.json'.format(nomination_id))

        output_dict = {
            str(nomination_id): {
                'title': title,
                'reviews': reviews,
            },
        }

        store_json(output_path, output_dict)

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

    r = http.request('GET', url, fields={'q': regulated_title})
    data = r.data.decode('utf-8')

    soup = BeautifulSoup(data, 'html.parser')

    id_title = []
    for element in soup.findAll("div", {"class": "li_pp"}):
        temp_id = re.sub(r'\D', '', element.a['href'])
        temp_title = element.find('div', {'class': 'li_ttl'}).string
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
        url = 'https://coco.to/movie/{}/review/{}'.format(select['cocoId'], str(i + 1))
        encoded_url = urllib.parse.quote(url, '/:?=&')
        r = http.request('GET', encoded_url)
        data = r.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        flag = False

        if len(soup.findAll('h2', {'class': 'tweet_title2'})) > 0:
            flag = True

        if len(soup.findAll('h2', {'class': 'tweet_title1'})) > 0:
            flag = True

        li = soup.findAll('li', {'class': 'tweet_li'})

        if len(li) == 0:
            flag = True

        for counter, each in enumerate(li):
            comment_string = each.find('div', {'class': 'tweet_text'}).next_element
            processed_comment = re.sub(r'\s', ' ', comment_string)
            date_element = each.find('div', {'class': 'updated'})
            date_string = date_element.a['title']
            date_string = re.search(r'\d\d\d\d:\d\d:\d\d', date_string).group().replace(':', '-')
            comments.append({'date': date_string, 'review': processed_comment})

        if flag:
            break

    return(comments)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4:
        print('disignate filepath')
        sys.exit(0)
    if len(args) == 4:
        main(args[1], args[2], args[3])
