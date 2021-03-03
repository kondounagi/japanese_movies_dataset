import re
import sys
import json
import requests
from bs4 import BeautifulSoup


def scrape_nominate_movie(year):
    film_index = "https://eiga.com/movie/"

    re_time = re.compile(r"／\d*分／")
    re_production_studio = re.compile(r"配給：[^<]*")
    re_title = re.compile(r"映画「[^」]*」")
    re_date = re.compile(r"\d*年\d*月\d*日")
    year_film_data = []

    # title aligns with eiga.com
    best_prize_title = [
        '万引き家族',
        '三度目の殺人',
        'シン・ゴジラ',
        '海街diary',
        '永遠の0',
        '舟を編む',
        '桐島、部活やめるってよ',
        '八日目の蟬',
        '告白',
        '沈まぬ太陽',
        'おくりびと',
        '東京タワー オカンとボクと、時々、オトン',
        'フラガール',
        'ALWAYS 三丁目の夕日',
        '半落ち',
        '壬生義士伝',
        'たそがれ清兵衛',
        '千と千尋の神隠し',
        '雨あがる',
        '鉄道員（ぽっぽや）',
        '愛を乞うひと',
        'もののけ姫',
        'Shall we ダンス？',
        '午後の遺言状',
        '忠臣蔵外伝 四谷怪談',
        '学校',
        'シコふんじゃった。',
        '息子',
        '少年時代',
        '黒い雨',
        '敦煌',
        'マルサの女',
        '火宅の人',
        '花いちもんめ',
        'お葬式',
        '楢山節考',
        '蒲田行進曲',
        '駅 STATION',
        'ツィゴイネルワイゼン',
        '復讐するは我にあり',
        '事件',
        '幸福の黄色いハンカチ',
    ]

    with open("nominate_id/" + str(year) + ".txt", "r") as f:
        for line in f.readlines():
            film_id = line.strip()
            film_data = {}

            film_data["director"] = []
            film_data["scriptwriter"] = []
            film_data["performers"] = []
            film_data["screen_time"] = -1
            film_data["production_studio"] = ""
            film_data["title"] = ""
            film_data["year"] = year
            if len(year_film_data) == 0 and year != 2020:
                film_data["prize"] = 1
            else:
                film_data["prize"] = 0
            # fetch top-1 movie result information
            content = requests.get(film_index + film_id).content
            soup = BeautifulSoup(content, features="lxml")

            # filter out screen time and production studio
            html_text = soup.prettify()
            production_studio = re_production_studio.search(html_text)
            screen_time = re_time.search(html_text)
            title = re_title.search(html_text)
            date = re_date.search(html_text)
            if production_studio:
                film_data["production_studio"] = (
                    production_studio.group(0)[3:].strip())
            if screen_time:
                film_data["screen_time"] = int(screen_time.group(0)[1:-2])
            if title:
                film_data["title"] = title.group(0)[3:-1]
                if film_data["title"] in best_prize_title:
                    film_data["prize"] = 1
            else:
                print(film_id)
            if date:
                date_str = date.group(0)
                film_data["year"] = date_str[0:date_str.find("年")]
                film_data["month"] = (
                    date_str[date_str.find("年") + 1:date_str.find("月")])
                film_data["day"] = (
                    date_str[date_str.find("月") + 1:date_str.find("日")])

            # filter out informative data
            staff_cast = soup.find(id="staff-cast")
            if staff_cast is not None:
                for div in staff_cast.find_all():
                    # When calling div["class"], return type is list[string]
                    if div.name == "dl" and div.has_attr("class") and div["class"][0] == "movie-staff":
                        # movie staff column
                        data_type = ""
                        for p in div.find_all():
                            if p.name == "dt":
                                if p.get_text().find("監督") != -1:
                                    data_type = "director"
                                elif p.get_text().find("脚本") != -1:
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

            # print(film_data)
            year_film_data.append(film_data)
            sys.stdout.flush()
    return year_film_data


def main(end_year=2020):
    start_year = 1978

    years_dict = {}
    unique_id = 1
    for i in range(start_year, end_year + 1):
        years_dict[i] = scrape_nominate_movie(i)
        for j in range(len(years_dict[i])):
            years_dict[i][j]["id"] = unique_id
            unique_id += 1
    with open("nominate_movie_meta_data.json", "w") as f:
        f.write(json.dumps(years_dict,
                           ensure_ascii=False,
                           sort_keys=True,
                           indent=4,
                           separators=(',', ': ')))
        f.write("\n")


if __name__ == "__main__":
    main(int(sys.argv[1]))
