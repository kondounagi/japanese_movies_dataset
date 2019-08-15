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
    url_search = ('https://eiga.com/search/{}'
                  .format(requests.utils.quote(normalize_query(q), safe='')))

    res_search = requests.get(url_search)
    res_search.encoding = res_search.apparent_encoding

    soup_search = BeautifulSoup(res_search.content, "lxml")
    result = soup_search.find('section', attrs={"id": "rslt-movie"})
    if result:
        path = result.find('li', attrs={"class": "col-s-3"}).find('a')["href"]
        url_review = 'https://eiga.com' + path
        return url_review
    else:
        return None


def scrape(query):
    data = {
        "id": -1,
        "rating": -1,
        "check-in": -1,
        "review-count": -1,
    }
    print("START : " + query)
    url_review = search(query)

    if url_review is None:
        logging.warning("**************************************************")
        logging.warning(query + " HAS NO RESULT")
        logging.warning("**************************************************")
        return None

    res = requests.get(url_review)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.content, "lxml")

    rating = soup.find('span', attrs={"class": "rating-star"})
    review_count = soup.find('span', attrs={"itemprop": "reviewCount"})
    check_in = soup.select_one("a.icon-movie-checkin").find('strong')

    if rating.text == '－':
        data["rating"] = 0
    else:
        data["rating"] = float(rating.text)

    if review_count is None:
        data["review-count"] = 0
    else:
        data["review-count"] = int(review_count.text)

    if check_in is None:
        data["check-in"] = 0
    else:
        data["check-in"] = int(check_in.text)

    return data


def main():
    with open('../2018_movie_clean', 'r') as movie_clean:
        for line in csv.reader(movie_clean, delimiter='\t'):
            movie_id, title, *_ = line
            output_file = './{}.json'.format(movie_id)
            with open(output_file, 'w') as f:
                print(movie_id)
                data = scrape(title)
                if data is None:
                    continue
                data["id"] = int(movie_id)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write('\n')
            time.sleep(1)


if __name__ == '__main__':
    main()
