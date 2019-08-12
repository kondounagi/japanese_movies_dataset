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


def concat_url_path(*args):
    str_args = [str(p) for p in args]
    url = '/'.join([p.strip('/') for p in str_args])

    if str_args[-1].endswith('/'):
        return url + '/'
    else:
        return url


def search(q):
    url_search = 'https://eiga.com/search/{}'.format(
        requests.utils.quote(normalize_query(q), safe=''))

    res_search = requests.get(url_search)
    res_search.encoding = res_search.apparent_encoding

    soup = BeautifulSoup(res_search.content, "lxml")
    result = soup.select_one('section#rslt-movie')

    if result:
        path = result.select_one('a[href^="/movie/"]')['href']
        url_review = concat_url_path('https://eiga.com/', path, '/review/all/')
        return url_review
    else:
        return None


def scrape_review(query):
    page_num = 1
    data = {
        "id": -1,
        "reviews": {
            "eigacom": [],
            "filmarks": [],
            "coco": [],
        }
    }

    print("START : " + query)
    url_review = search(query)

    if url_review is None:
        logging.warning("**************************************************")
        logging.warning(query + " HAS NO RESULT")
        logging.warning("**************************************************")
        return None

    while(1):
        res = requests.get(concat_url_path(url_review, page_num))
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, "lxml")
        reviews = soup.select('div.user-review')

        # ページ数の上限を超えたら
        if not reviews:
            print('DONE : ' + query )
            break

        for r in reviews:
            title = r.select_one('h2.review-title a')
            main_text = r.select_one('div.txt-block')
            tgl_btn = main_text.select_one('div.toggle-btn')

            if tgl_btn:
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
