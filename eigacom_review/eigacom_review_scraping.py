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
    if(result is not None):
        path = result.find('li', attrs={"class": "col-s-3"}).find('a')["href"]
        url_review = 'https://eiga.com' + path + 'review/all/'
        return url_review
    else:
        print("**************************************************")
        print(q + " HAS NO RESULT")
        print("**************************************************")
        return "error"

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
    url_review=search(query)

    if(url_review == "error"):
        return "error"

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


input_file = '../2018_movie_clean'
for q in open(input_file, 'r', encoding='utf-8').readlines():
    movie_id = int(q.split()[0])
    output_file = './{0}.json'.format(movie_id)
    with open(output_file, 'w') as f:
        data = scrape_review(q)
        if(data == "error"):
            continue
        data["id"] = movie_id
        jsn =  json.dumps(data,ensure_ascii=False, indent=2)
        f.write(jsn)
    f.close()
