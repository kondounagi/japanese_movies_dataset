import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Search hit numbers of Google Search

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--titles", default="../2018_movie_clean", help="path of the titles list", type=str)
args = parser.parse_args()

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

path = args.titles
search_count_list = []
with open(path) as f:
    for line in f:
        search_count_element = {}
        word = line.split('\t')[1]
        url = "https://www.google.com/search?q={}&safe=off".format(word + " 映画")
        driver.get(url)
        time.sleep(10)
        search_count_element["title"] = word
        for i in range(3):  # Retry twice
            try:
                stats = driver.find_element_by_id("resultStats").text.split(' ')[1]

                # print(word + " : " + stats)
                # print("=======================")
                search_count_element["search_count"] = stats
                search_count_list.append(search_count_element)
                break
            except NoSuchElementException as exception:
                next_arrow = driver.find_element_by_css_selector("#navcnt table td.cur + td a")
                next_arrow.click()
                driver.refresh()
                time.sleep(10)
        else:
            search_count_element["search_count"] = ""
            search_count_list.append(search_count_element)
            print("NoSuchElementException: " + word)

output = open('./search_count_new.json', 'w')
json.dump(search_count_list, output, ensure_ascii=False, indent=4, separators=(',', ':'))

driver.quit()
