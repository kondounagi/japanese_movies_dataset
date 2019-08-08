import requests  
import os
import sys 
import re 
import json 
from bs4 import BeautifulSoup 

'''
data to be stored from eiga.com

title: string
director: array[string]
scriptwriter: array[string]
performers: array[string]
screen_time: -1
production_studio: string
'''

def main():
    film_index = "https://eiga.com"
    film_search = "https://eiga.com/search/"
    # regular experssion for finding time and studio
    re_time = re.compile("／\d*分／")
    re_production_studio = re.compile("配給：[^<]*")
    start_num = 0         # in case of connection refused

    # films_data = []     # ditionary list
    fail_list = []
    with open("2018_movie_clean", 'r') as clean_file:
        film_list = clean_file.readlines()
        film_num = 0
        for film in film_list:
            film_num += 1
            if (film_num < start_num):
                continue 

            # filter out movie title
            film_splits = film.split() 
            film = ""
            for i in range(len(film_splits) - 3):
                film += film_splits[i] 
            
            # initilize single film dictionary
            film_data = {} 
            film_data["title"] = film 
            film_data["director"] = []
            film_data["scriptwriter"] = []
            film_data["performers"] = []
            film_data["screen_time"] = -1
            film_data["production_studio"] = ""

            # fetch search result
            content = requests.get(film_search + film).content
            soup = BeautifulSoup(content, features = "lxml") 
            if (soup.find(id = "rslt-movie") == None):
                fail_list.append(film_num)
                continue
            film_id = soup.find(id = "rslt-movie").find_all("a")[1]['href']
            
            # fetch top-1 movie result information
            content = requests.get(film_index + film_id).content 
            soup = BeautifulSoup(content, features = "lxml") 
            
            # filter out screen time and production studio
            html_text = soup.prettify()
            production_studio = re_production_studio.search(html_text) 
            screen_time = re_time.search(html_text)
            if production_studio:
                film_data["production_studio"] = production_studio.group(0)[3:].strip()
            else:
                print("no match studio")
            if screen_time:
                film_data["screen_time"] = int(screen_time.group(0)[1:-2])
            else:
                print("no match time")
            # filter out informative data 
            staff_cast = soup.find(id = "staff-cast") 
            for div in staff_cast.find_all():
                # When calling div["class"], return type is list[string]
                if div.name == "dl" and div.has_attr("class") and div["class"][0] == "movie-staff":
                    # movie staff column
                    data_type = ""
            
                    for p in div.find_all():
                        if p.name == "dt":
                            if p.get_text() == "監督":
                                data_type = "director"
                            elif p.get_text() == "脚本":
                                data_type = "scriptwriter"
                            else: 
                                data_type = ""    
                            # new meta data type can be added here
                            
                        elif p.name == "dd" and len(data_type) > 0:
                            film_data[data_type].append(p.get_text().strip())
                elif div.name == "ul" and div.has_attr("class") and div["class"][0] == "movie-cast":
                    # movie cast column
                    for p in div.find_all():
                        if p.name == "span":
                            film_data["performers"].append(p.get_text().strip())
            print(film_num, film_data) 
            with open("meta_movie_data/" + str(film_num), "w") as output_file:
                json.dump(film_data, output_file)
            # break 
    print(fail_list)

            
       

if __name__ == "__main__":
    main() 

