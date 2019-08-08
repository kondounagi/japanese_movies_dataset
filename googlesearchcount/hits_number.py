import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import json

# Search hit numbers of Google Search

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

path = "../2018_movie_clean"
search_count_map = {}
with open(path) as f:
    for line in f:
        word = line.split('\t')[0]
        url = "https://www.google.com/search?q={}&safe=off".format(word + " 映画")
        driver.get(url)
        time.sleep(10)
        try:
            stats = driver.find_element_by_id("resultStats").text.split(' ', 3)[1]

            # print(word + " : " + stats)
            # print("=======================")
            search_count_map[word] = stats
        except NoSuchElementException as exception:
            print("NoSuchElementException: " + word)


output = open('./search_count.json', 'w')
json.dump(search_count_map, output, ensure_ascii=False)

driver.quit()
