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
    titles = []
    with open(filepath, 'r', encoding="utf-8_sig") as f:
        reader = csv.reader(f,delimiter = '\t')
        for row in reader:
            title = row[0]
            titles.append(title)

    for i in range(len(titles)):
        title = titles[i]
        select = getCocoId(title)
        comments = getCocoReview(select)
        comment_dict = {'title':title, 'comments': comments}
        output = open('./{}.json'.format(str(i+1)), 'w', encoding = 'utf-8')
        json.dump(comment_dict, output, indent = 4, ensure_ascii = False)
        output.close()

    return

def getCocoId(title):
    
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
            '？': '?'
        })
        regulated_title = re.sub(r'（[^（）]*）', '', title_string)
        regulated_title = re.sub(r'\([^\(\)]*\)', '', regulated_title)
        regulated_title = re.sub(r'[\s\-～〜:：;、。<>＜＞「」\"\',\.・/／－]+', ' ', regulated_title)
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

    return select

def getCocoReview(select):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    url = 'https://coco.to/movies'

    comments = []
    if select == None:
        return comments

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
