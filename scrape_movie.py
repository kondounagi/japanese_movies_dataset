import csv
import requests
import os
import sys
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

'''
    meta data to be stored from eiga.com

    title: string
    director: array[string]
    scriptwriter: array[string]
    performers: array[string]
    screen_time: -1
    production_studio: string
    date: yyyy-mm-dd
'''


def fetch_film_id(film, year, month, day):

    url = "https://www.bing.com/search"
    movie_re = re.compile(r"/movie/\d{5}/")

    query = ' '.join(['site:https://eiga.com/movie/', film, year, month, day])
    page = requests.get(url, params={'q': query})

    film_id = movie_re.search(page.text)
    # print(soup.prettify())
    if film_id is None:
        return ""
    else:
        return film_id.group(0)


def clean_paren(text):
    """Remove nested parentheses from text.

    >>> clean_paren( 'アンダー・ザ・ウォーター（ スウェーデン・ デンマーク・ フィンランド）')
    'アンダー・ザ・ウォーター'

    >>> clean_paren( '葡萄畑に帰ろう (ジョージア (国)の旗 ジョージア)')
    '葡萄畑に帰ろう '

    >>> clean_paren('(r)adius ラディウス（英語版）')  # OMG
    'adius ラディウス'
    """
    left_parenthese = 0
    right_parenthese = 0

    saved = []
    for char in text:
        if char == "(" or char == "（":
            left_parenthese += 1
        elif char == ")" or char == "）":
            right_parenthese += 1
        elif right_parenthese >= left_parenthese:
            saved.append(char)

    return ''.join(saved)


def main():
    year = sys.argv[1]

    film_index = "https://eiga.com"
    # regular experssion for finding time and studio
    re_time = re.compile("／\\d*分／")
    re_production_studio = re.compile("配給：[^<]*")
    start_num = 0         # in case of connection refused

    # films_data = []     # ditionary list
    fail_list = []
    id_list = []

    with open(year + "_movie_clean", 'r') as clean_file:
        reader = csv.reader(clean_file, delimiter='\t')
        for film_num, film, year, month, day in reader:
            if (int(film_num) < start_num):
                continue

            print(film_num, film)

            dt = datetime(int(year), int(month), int(day))

            # initilize single film dictionary
            film_data = {}
            film_data["title"] = film
            film_data["director"] = []
            film_data["scriptwriter"] = []
            film_data["performers"] = []
            film_data["screen_time"] = -1
            film_data["production_studio"] = ""
            film_data["release_date"] = dt.strftime("%Y-%m-%d")

            film = clean_paren(film)

            film = re.sub(r'''
                (?:
                    [!?"#$%&'()*+,-./\:;<=>@|~^_`]  # ascii signs
                    |[，。★、…！？]                 # fullwidth
                    |[“”‘’[]{}【】《》]             # brace
                    |\s                             # space
                )+
            ''', "", film, flags=re.VERBOSE)

            # fetch search result
            film_id = fetch_film_id(film, year, month, day)
            if len(film_id) == 0:
                fail_list.append(film_num)
                id_list.append(-1)
                continue
            id_list.append(int(film_id[7:12]))

            # this only used for small fix
            # film_id = "/movie/88817/"

            # fetch top-1 movie result information
            content = requests.get(film_index + film_id).content
            soup = BeautifulSoup(content, features="lxml")

            # filter out screen time and production studio
            html_text = soup.prettify()
            production_studio = re_production_studio.search(html_text)
            screen_time = re_time.search(html_text)

            if production_studio:
                film_data["production_studio"] = (production_studio
                                                  .group(0)[3:].strip())

            if screen_time:
                film_data["screen_time"] = int(screen_time.group(0)[1:-2])

            # filter out informative data
            staff_cast = soup.find(id="staff-cast")
            if staff_cast is not None:
                ms = staff_cast.select_one('dl.movie-staff')
                if ms:
                    staff = {role.get_text().strip(): name.get_text().strip()
                             for role, name in zip(ms.select('dt'),
                                                   ms.select('dd'))}

                    if '監督' in staff:
                        film_data['director'].append(staff['監督'])

                    if '脚本' in staff:
                        film_data['scriptwriter'].append(staff['脚本'])

                mc = staff_cast.select_one('ul.movie-cast')
                if mc:
                    performers = [name.get_text().strip()
                                  for name in mc.select('span')]

                    film_data['performers'].extend(performers)

            print(film_num, film_data)

            output_filepath = os.path.join("meta_movie_data",
                                           str(dt.year),
                                           str(film_num) + ".json")
            with open(output_filepath, "w") as output_file:
                json.dump(film_data, output_file, ensure_ascii=False)
                output_file.write('\n')
            print(fail_list)
            sys.stdout.flush()

    with open("myid_to_eigaid", "a") as id_file:
        for i in range(len(id_list)):
            id_file.write("\t".join([year, str(i + 1), str(id_list[i])]))
            id_file.write("\n")


if __name__ == "__main__":
    main()
