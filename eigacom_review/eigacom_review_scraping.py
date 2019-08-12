import csv
import logging
import requests
from bs4 import BeautifulSoup
import time
import re
import json

logging.basicConfig(format='%(message)s')

def normalize_query(q):
    q = q.replace('\n', '')
    q = q.replace('（', '(')
    q = q.replace('）', ')')
    q = re.sub(r"\(.+\)$", "", " ".join(q))
    q = re.sub('(!|\u3000|/|\\s|>|<|\\.)+', " ", q)
    return q

def search(q):
    url_search = 'https://eiga.com/search/{}'.format(
        requests.utils.quote(normalize_query(q), safe=''))

    res_search = requests.get(url_search)
    res_search.encoding = res_search.apparent_encoding

    soup_search = BeautifulSoup(res_search.content, "lxml")
    result =  soup_search.find('section', attrs={"id": "rslt-movie"})

    if result:
        path = result.find('li', attrs={"class": "col-s-3"}).find('a')["href"]
        url_review = 'https://eiga.com' + path + 'review/all/'
        return url_review
    else:
        return None

def scrape_review(query):
    page_num = 1
    data = {
        "id": -1,
        "reviews":{
            "eigacom":[],
            "filmarks":[],
            "coco":[],
        }
    }

    print("START : " + query)
    url_review=search(query)

    if url_review is None:
        logging.warning("**************************************************")
        logging.warning(query + " HAS NO RESULT")
        logging.warning("**************************************************")
        return None

    while(1):
        res = requests.get(url_review + str(page_num))
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, "lxml")
        if soup.find('div', attrs={"class": "user-review"}) == None: # ページ数の上限を超えたら
            print('DONE : ' + query )
            break

        for r in soup.find_all('div', attrs={"class": "user-review"}):
            title = r.find('h2',attrs={"class": "review-title"}).find('a')
            main_text =  r.find('div',attrs={"class": "txt-block"})
            tgl_btn = main_text.find('div',attrs={"class": "toggle-btn"})
            if tgl_btn is not None:
                tgl_btn.decompose()
            d = title.text + "\n" +  main_text.text.replace("\n", "")
            data["reviews"]["eigacom"].append(d)
        page_num += 1
        time.sleep(1)
    return data


def main():
    with open('../2018_movie_clean', 'r') as movie_clean:
        for line in csv.reader(movie_clean, delimiter='\t'):
            movie_id, title, *_ = line
            output_file = './{}.json'.format(movie_id)
            with open(output_file, 'w') as f:
                data = scrape_review(title)
                if data is None:
                    continue
                data["id"] = int(movie_id)
                json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
