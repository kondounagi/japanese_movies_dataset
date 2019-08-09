#!/usr/bin/env python3
import certifi
import urllib3
import urllib
from bs4 import BeautifulSoup
import re
import csv
import sys
import json

def main(filepath,start_row = 1,end_row = None):
    titles = []
    with open(filepath, 'r', encoding="utf-8_sig") as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            title = row[0]
            titles.append(title)

    if end_row != None:
        if end_row > len(titles):
            end_row = len(titles)
    else:
        end_row = len(titles)
    
    for i in range(start_row-1,end_row):
        title = titles[i]
        select = getCocoId(title)
        comments = getCocoReview(select)
        data = getCocoData(select)
        comment_dict = {
            'title': title,
            'id': i,
            'data': {'eigacom': [], 'filmarks': [], 'coco': data},
            'reviews': {'eigacom': [], 'filmarks': [], 'coco': comments}
        }
        output = open('./{}.json'.format(str(i + 1)), 'w', encoding='utf-8')
        json.dump(comment_dict, output, indent=4, ensure_ascii=False)
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

    if select is None and len(id_title) is not 0:
        select = id_title[0]

    return select

def getCocoReview(select):
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
        for counter, each in enumerate(li):
            comment_string = each.find('div', {'class': 'tweet_text'}).next_element
            processed_comment = re.sub(r'\s', ' ', comment_string)
            comments.append(processed_comment)

        if flag:
            break

    return(comments)

def getCocoData(select):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    url = 'https://coco.to/movies'

    data_dict = {'satisfaction': None,
                 'whole_tweet_amount': None,
                 'each_tweet_amount': {
                     'good': None,
                     'even': None,
                     'bad': None
                 },
                 'positive_index': None,
                 'review_word': []
                }
    if select == None:
        return data_dict
    
    url = 'https://coco.to/movie/{}'.format(select['cocoId'])
    encoded_url = urllib.parse.quote(url, '/:?=&')
    r = http.request('GET', encoded_url)
    data = r.data.decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    
    satisfaction_element = soup.find('span', {'style': 'font-size:45px;margin-right:5px'})
    data_dict['satisfaction'] = int(satisfaction_element.string) if satisfaction_element != None else None
    
    review_good_element = soup.find('div' , {'class': 'review_good'}).nextSibling
    data_dict['each_tweet_amount']['good'] = int(review_good_element.string.replace(',','')) if review_good_element != None else None
    
    review_even_element = soup.find('div', {'class': 'review_even'}).nextSibling
    data_dict['each_tweet_amount']['even'] = int(review_even_element.string.replace(',','')) if review_even_element != None else None
    
    review_bad_element = soup.find('div', {'class': 'review_bad'}).nextSibling
    data_dict['each_tweet_amount']['bad'] = int(review_bad_element.string.replace(',','')) if review_bad_element != None else None
    
    tweet_amount_element = soup.find('span', {'style': 'font-size:17px;margin-right:2px'})
    data_dict['whole_tweet_amount'] = int(tweet_amount_element.string.replace(',','')) if tweet_amount_element != None else None
    
    positive_index_element = soup.find('span', {'style': 'font-size:15px;margin:0 2px 0 3px'})
    data_dict['positive_index'] = int(positive_index_element.string) if positive_index_element != None else None
    
    review_keyword_wrapper = soup.find('div', {'class': 'tag_list clearflt clearboth'})
    review_keyword_elements = review_keyword_wrapper.findAll('a') if review_keyword_wrapper is not None else []

    for element in review_keyword_elements:
        keyword_dict = {'keyword': None, 'grade': None}
        keyword_dict['keyword'] = element.string
        m = re.search(r'font\-size:\d+px',element['style'])
        font_size_style = m.group()
        size = re.sub(r'\D','',font_size_style)
        mapping = {'10':'少し','19':'まあまあ','24':'とても'}
        keyword_dict['grade'] = mapping.get(size,'不明')
        data_dict['review_word'].append(keyword_dict)    
    
    return data_dict

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('disignate filepath')
        sys.exit(0)
    if len(args) == 2:
        main(args[1])
    if len(args) == 3:
        main(args[1], start_row = int(args[2]) )
    if len(args) == 4:
        main(args[1], start_row = int(args[2]), end_row = int(args[3]))
