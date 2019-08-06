import requests  
import os
import sys 
from bs4 import BeautifulSoup 

filmarks_query = "https://eiga.com/search/"
clean_file = open("2018_movie_clean", 'r')
film_list = clean_file.readlines()

for film in film_list: 
    print(film)
    content = requests.get(filmarks_query + film).content
    # print(content)
    soup = BeautifulSoup(content, features="lxml") 
    # soup = soup.prettify()
    print(soup.find(id = "rslt-movie"))

    break




