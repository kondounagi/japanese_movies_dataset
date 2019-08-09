import requests
from bs4 import BeautifulSoup
import time
import re
import json

def search(q):
    q = q.replace('\n', '').replace('（', '(').replace('）', ')')
    print("START : " + q)
    q = re.sub("\(.+\)$", "", " ".join(q.split()[1:-3]), re.UNICODE)
    query = re.sub('(!|\u3000|/|\s|>|<|\.)+', "%20", q)
    url_search = 'https://eiga.com/search/' + query
    res_search = requests.get(url_search )
    res_search.encoding = res_search.apparent_encoding
    soup_search = BeautifulSoup(res_search.content, "lxml")
    result =  soup_search.find('section', attrs={"id": "rslt-movie"})
    if(result != None):
        path = result.find('li', attrs={"class": "col-s-3"}).find('a')["href"]
        url_review = 'https://eiga.com' + path
        return url_review
    else:
        print("**************************************************")
        print(q + " HAS NO RESULT")
        print("**************************************************")
        return "error"

def scrape(query):
    page_num = 1
    data = {
        "id": -1,
        "rating": -1,
        "check-in":-1,
        "review-count":-1
    }
    url_review=search(query)

    if(url_review == "error"):
        return "error"

    res = requests.get(url_review)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.content, "lxml")

    rating = soup.find('span', attrs={"class": "rating-star"})
    review_count = soup.find('span', attrs={"itemprop": "reviewCount"})
    check_in = soup.find('a', attrs={"class": "icon-movie-checkin"}).find('strong')
    data["rating"] = 0 if rating.text == '－' else float(rating.text)
    data["review-count"] = 0 if review_count is None else int(review_count.text)
    data["check-in"] = 0 if check_in is None else int(check_in.text)

    return data

input_file = '../2018_movie_clean'
for q in open(input_file, 'r', encoding='utf-8').readlines():
    movie_id = int(q.split()[0])
    output_file = './{0}.json'.format(movie_id)
    with open(output_file, 'w') as f:
        data = scrape(q)
        if(data == "error"):
            continue
        data["id"] = movie_id
        jsn =  json.dumps(data,ensure_ascii=False, indent=2)
        f.write(jsn)
    f.close()
    time.sleep(1)
