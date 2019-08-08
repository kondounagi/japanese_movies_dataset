#!/usr/bin/env python3
import certifi
import urllib3
import urllib
from bs4 import BeautifulSoup
import re
import csv
import sys
import json

def main(filepath):
    comment_dict = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f,delimiter = '\t')
        for row in reader:
            title = row[0]
            comments = cocoScraping(title)
            comment_dict = {'title': title, 'comments': comments}
    
    output = open('./coco_review.json', 'w')
    json.dump(comment_dict, output, ensure_ascii=False)
    return


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

        temp_title = re.sub(r'\([^\(\)]*\)', "", temp_title)
        temp_title = temp_title.replace('...', '')
        element['title'] = temp_title

    regulated_title = re.sub(r'\s', ' ', title)
    regulated_title = re.sub(r'（[^（）]*）', "", regulated_title)
    regulated_title = re.sub(r'\([^\(\)]*\)', "", regulated_title)
    regulated_title = regulated_title.replace('...', '')

    select = None

    for element in id_title:
        min_length = min(len(element['title']), len(regulated_title))
        if regulated_title[:min_length] == element['title'][:min_length]:
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
            comment_string = each.find('div', {'class': 'tweet_text'}).next_element
            processed_comment = re.sub(r'\s',' ',comment_string)
            comments.append(processed_comment)

        if flag:
            break

    return(comments)

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('disignate filepath')
        sys.exit(0)
    main(args[1])