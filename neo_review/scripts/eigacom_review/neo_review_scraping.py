#!/usr/bin/env python
# coding: utf-8

# In[29]:


import csv
import logging
logging.basicConfig(format='%(message)s')
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import datetime


# In[30]:


def scrape_review(eigacom_id):
    page_num = 1
    
    data = {
        "title" : -1,
        "reviews" : []
    }
    
    rating_dict = {"val00":0.0, "val05":0.5,"val10":1.0,"val15":1.5,"val20":2.0,"val25":2.5,"val30":3.0,"val35":3.5,"val40":4.0,"val45":4.5,"val50":5.0}
    
    print("START : " + eigacom_id)
    url_review='https://eiga.com/movie/' + eigacom_id + '/review/all/'
    
    if url_review is None:
        logging.warning("**************************************************")
        logging.warning(q + " HAS NO RESULT")
        logging.warning("**************************************************")
        return None
    
    while(1):
        res = requests.get(url_review + str(page_num))
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.content, "lxml")
        
        if page_num == 1:
            title = soup.find('p', attrs={"class":"title-link"}).text
            data["title"] = title
            
        if soup.find('div', attrs={"class": "user-review"}) == None: # ページ数の上限を超えたら
            print('DONE : ' + eigacom_id )
            break
            
        for r in soup.find_all('div', attrs={"class": "user-review"}):
            review_title = r.find('h2',attrs={"class": "review-title"})
            title = review_title.find('a')
            
            rating_class = review_title.find('span',attrs={"class": "rating-star"}).get('class')[1]
            rating = rating_dict[rating_class]
            
            empathy = r.find('div', attrs={"class": "empathy"}).find(('strong')).text
            
            date= r.find('div',attrs={"class": "review-data"}).find('div',attrs={"class": "time"})
            main_text =  r.find('div',attrs={"class": "txt-block"})
            
            tgl_btn = main_text.find('div',attrs={"class": "toggle-btn"})
            if tgl_btn is not None:
                tgl_btn.decompose()
            
            item = {
                "date" : "",
                "rating" : rating,
                "empathy" : int(empathy),
                "review" : "",
            }
            
            review_text = title.text + "\n" +  main_text.text.replace("\n", "")
            item["review"] = review_text
            
            y, m, d, _ = re.split('[年月日]', date.text)
            item["date"] = str(datetime.date(int(y), int(m), int(d)))
            
            data["reviews"].append(item)
            
        page_num += 1
        time.sleep(1)
    return data


# In[32]:


def main():
    
    data_all = {}
    
    movie_id = 1
    
    for year in range(1978, 2020):
        print(year)
        with open('./eigacom_nomination_id_table/{}.txt'.format(str(year)), 'r') as id_table:
            for line in csv.reader(id_table):
                if line == "\n":
                    continue
                eigacom_id, *_ = line
                
                print(movie_id)
                data = scrape_review(eigacom_id)
                
                if data == None:
                    movie_id += 1
                    continue
                data_all[str(movie_id)] = data
                movie_id += 1

    output_file = '../../data/eigacom_review.json'
    with open(output_file, 'w') as f:
        json.dump(data_all, f, ensure_ascii=False, indent=2)


# In[33]:


if __name__ == "__main__":
    main()


# In[ ]:




