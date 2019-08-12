import re
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import urlencode

# Search hit numbers of Google Search

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--titles",
                    default="../2018_movie_clean",
                    help="path of the titles list",
                    type=str)
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

        url = "https://www.google.com/search"
        url += "?" + urlencode({
            'q': ' '.join([word, "映画"]),
            'safe': "off",
        })

        driver.get(url)
        time.sleep(10)

        # Retry just once
        for _ in range(2):
            try:
                result_stats = driver.find_element_by_id("resultStats").text

                search = re.search('About ([0-9,]+) results', result_stats)
                if search:
                    count = search.group(1)

                    search_count_element["title"] = word
                    search_count_element["search_count"] = count
                    search_count_list.append(search_count_element)
                    break
            except NoSuchElementException as exception:
                driver.refresh()
                time.sleep(10)
        else:
            search_count_element["title"] = word
            search_count_element["search_count"] = ""
            search_count_list.append(search_count_element)
            print("NoSuchElementException: " + word)

with open('./search_count_new.json', 'w') as output:
    json.dump(search_count_list, output,
              ensure_ascii=False,
              indent=4,
              separators=(',', ':'))

driver.quit()
