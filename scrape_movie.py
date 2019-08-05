import requests  
import os
import sys 
from bs4 import BeautifulSoup 

filmarks_query = "https://filmarks.com/search/movies?q="
clean_file = open(sys.argv[1], 'r')
film_list = clean_file.readlines()

for film in film_list: 
    content = requests.get(filmarks_query + film).content
    # print(content)
    soup = BeautifulSoup(content, features="lxml") 
    soup = soup.prettify()
    print(soup.html)
    break




