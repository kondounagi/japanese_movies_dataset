#!/usr/bin/env python3
import asyncio
import aiohttp
import urllib
from bs4 import BeautifulSoup
import re
import sys
import json
import os


def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)


def store_json(filepath, obj):
    with open(filepath, 'w') as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)
        f.write('\n')


async def main(filepath: str, output_dir: str, year):
    meta_data = load_json(filepath)

    # Just like Chrome does
    connector = aiohttp.TCPConnector(limit_per_host=6)

    async with aiohttp.ClientSession(connector=connector) as session:
        stmts = [store_review_for(data, session, output_dir)
                 for data in meta_data[year]]
        await asyncio.gather(*stmts)


async def store_review_for(element, session, output_dir):
    nomination_id = element['id']
    title = element['title']

    select = await get_coco_id(session, title)
    reviews = await get_coco_review(session, select)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, '{}.json'.format(nomination_id))

    output_dict = {
        str(nomination_id): {
            'title': title,
            'reviews': reviews,
        },
    }

    store_json(output_path, output_dict)

    return True


async def get_coco_id(session, title):
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

    url = 'https://coco.to/movies'
    regulated_title = trans(title)

    async with session.get(url, params={'q': regulated_title}) as response:
        print(f"{response.status}: {response.url}")
        data = await response.text()
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


async def get_coco_review_page(session, select, i):
    url = ('https://coco.to/movie/{}/review/{}'
           .format(select['cocoId'], str(i + 1)))

    encoded_url = urllib.parse.quote(url, '/:?=&')
    async with session.get(encoded_url) as response:
        print(f"{response.status}: {response.url}")
        return await response.text()


async def get_coco_review(session, select):
    comments = []
    if select is None:
        return comments

    for i in range(200):
        data = await get_coco_review_page(session, select, i)
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
            date_element = each.select_one('div.updated')

            match = re.search(r'\d{4}:\d{2}:\d{2}', date_element.a['title'])
            if match:
                date_string = match.group().replace(':', '-')
            else:
                date_string = '1970-01-01'  # epoch as fallback

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
        asyncio.run(main(args[1], args[2], args[3]))
