#!/usr/bin/env python3
import certifi
import urllib3
import urllib
from bs4 import BeautifulSoup
import re


def cocoScraping(title):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    url = 'https://coco.to/movies'

    r = http.request('GET', url, fields={'q': title})
    data = r.data.decode('utf-8')

    soup = BeautifulSoup(data, 'html.parser')

    id_title = []
    for element in soup.findAll("div", {"class": "li_pp"}):
        temp_id = re.sub(r'\D', '', element.a['href'])
        temp_title = element.find('div', {'class': 'li_ttl'}).string
        id_title.append({'cocoId': temp_id, 'title': temp_title})

    for element in id_title:
        temp_title = element['title']
        temp_title = re.sub(r'\s', ' ', temp_title)

        temp_title = re.sub(r'（[^（）]*）', "", temp_title)

        temp_title = re.sub(r'\([^()]*\)', "", temp_title)
        temp_title = temp_title.replace('...', '')
        element['title'] = temp_title

    regulated_title = re.sub(r'\s', ' ', title)
    regulated_title = re.sub(r'（[^（）]*）', "", regulated_title)
    regulated_title = re.sub(r'\([^()]*\)', "", regulated_title)
    regulated_title = regulated_title.replace('...', '')

    select = None

    for element in id_title:
        if regulated_title[:len(element['title'])] == element['title']:
            select = element
            break

    comments = []

    for i in range(20):
        url = 'https://coco.to/movie/{}/review/{}'.format(select['cocoId'], str(i + 1))
        encoded_url = urllib.parse.quote(url, '/:?=&')
        r = http.request('GET', encoded_url)
        data = r.data.decode('utf-8')
        soup = BeautifulSoup(data, 'html.parser')

        flag = False

        if len(soup.findAll('h2', {'class': 'tweet_title2'})) > 0:
            flag = True

        li = soup.findAll('li', {'class': 'tweet_li'})
        for counter, each in enumerate(li):
            comment = each.find('div', {'class': 'tweet_text'}).next_element.replace('\n', '').replace('\u3000', ' ').replace('\r', '')
            comments.append(comment)

        if flag:
            break

    return(comments)
