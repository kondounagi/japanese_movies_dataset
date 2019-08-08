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

    idTitle = []
    for element in soup.findAll("div", {"class": "li_pp"}):
        tempId = re.sub(r'\D', '', element.a['href'])
        tempTitle = element.find('div', {'class': 'li_ttl'}).string
        idTitle.append({'cocoId': tempId, 'title': tempTitle})

    for element in idTitle:
        tempTitle = element['title']
        tempTitle = re.sub(r'\s', ' ', tempTitle)

        tempTitle = re.sub(r'（[^（）]*）', "", tempTitle)

        tempTitle = re.sub(r'\([^()]*\)', "", tempTitle)
        tempTitle = tempTitle.replace('...', '')
        element['title'] = tempTitle

    regulatedTitle = re.sub(r'\s', ' ', title)
    regulatedTitle = re.sub(r'（[^（）]*）', "", regulatedTitle)
    regulatedTitle = re.sub(r'\([^()]*\)', "", regulatedTitle)
    regulatedTitle = regulatedTitle.replace('...', '')

    select = None

    for element in idTitle:
        if regulatedTitle[:len(element['title'])] == element['title']:
            select = element
            break

    comments = []

    for i in range(20):
        url = 'https://coco.to/movie/{}/review/{}'.format(select['cocoId'], str(i + 1))
        encodedUrl = urllib.parse.quote(url, '/:?=&')
        r = http.request('GET', encodedUrl)
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
