#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import logging
logging.basicConfig(format='%(message)s')
import requests
from bs4 import BeautifulSoup
import time
import re


# In[13]:


def scrape(year):    
    
    print("START : " + str(year))
    url_nominate='https://eiga.com/award/japan-academy/' + str(year)
    


    res = requests.get(url_nominate)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.content, "lxml")
    
    table = soup.find('table', attrs={"class":"_a"})
    
    ids = []
    
    winner = table.find('tr', attrs={"class": "prize"})
    winner_path = winner.find('a')["href"]
    winner_id = re.sub("\\D", "", winner_path)
    ids.append(winner_id)
    winner.decompose()
    
    for a in table.find_all('a'):
        path = a["href"]
        id = re.sub("\\D", "", path)
        ids.append(id)
        
        time.sleep(1)
    return ids


# In[15]:


def main():
    for year in range(1978, 2000):
        ids = scrape(year)
        with open('{}.txt'.format(str(year)), 'w') as f:
            for id in ids:
                f.write(str(id) + "\n")


# In[16]:


if __name__ == "__main__":
    main()


# In[ ]:




