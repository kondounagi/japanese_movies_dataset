import json
import pandas as pd
import re
from sklearn.preprocessing import MultiLabelBinarizer
from collections import Counter
import sys


def json2dataframe(year):
    year_list = [str(year) for year in range(1978, int(year) + 1)]

    data = []
    with open('../nominate_movie_meta_data.json', 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
        for year in year_list:
            data += json_dict[year]

    data = pd.DataFrame(data).set_index('id')

    def dict2list_other_nominate(series):
        lst = []
        nullfrag = series.isnull().get('other_nominates')
        if nullfrag is False:
            other_nominates = series.get('other_nominates')
            for each in other_nominates:
                if type(each) is str:
                    lst.append(each)
                elif type(each) is dict:
                    if each['prized'] == 1:
                        lst.append(each['award'])
        return pd.Series([lst])

    data['other_nominates'] = data.apply(dict2list_other_nominate, axis = 'columns')

    data['production_studio'] = data['production_studio'].map(lambda each: re.split(r'[、＝=]',each))

    mlb = MultiLabelBinarizer()
    onehot = mlb.fit_transform(data['other_nominates'])
    columns = mlb.classes_
    nomination_onehot = pd.DataFrame(onehot, columns = columns, index = data.index) #####################

    performers = []
    data['performers'].map(lambda each: performers.extend(each))

    count = Counter(performers)
    countSeries = pd.Series(count)
    selected_performers = countSeries[countSeries > 9].index ######10回以上受賞作品に出演

    data['selected_performers'] = data['performers'].map(lambda each: list( set(each) & set(selected_performers) ))

    onehot = mlb.fit_transform(data['selected_performers'])
    columns = mlb.classes_
    selected_performers_onehot = pd.DataFrame(onehot, columns = columns, index = data.index) #####################10回以上出た出演者のonehot


    directors = []
    data['director'].map(lambda each: directors.extend(each))

    count = Counter(directors)
    countSeries = pd.Series(count)
    selected_directors = countSeries[countSeries > 3].index

    data['selected_directors'] = data['director'].map(lambda each: list( set(each) & set(selected_directors) ))

    onehot = mlb.fit_transform(data['selected_directors'])
    columns = mlb.classes_
    selected_directors_onehot = pd.DataFrame(onehot, columns = columns, index = data.index) #####################4回以上出た監督のonehot

    studio = []
    data['production_studio'].map(lambda each: studio.extend(each))

    count = Counter(studio)
    countSeries = pd.Series(count)
    selected_studios = countSeries[countSeries > 20].index ########################### 20回以上受賞

    data['selected_studio'] = data['production_studio'].map(lambda each: list( set(each) & set(selected_studios) ))

    onehot = mlb.fit_transform(data['selected_studio'])
    columns = mlb.classes_
    selected_studio_onehot = pd.DataFrame(onehot, columns = columns, index = data.index) #####################4回以上出た監督のonehot

    scriptwriters = []
    data['scriptwriter'].map(lambda each: scriptwriters.extend(each))

    count = Counter(scriptwriters)
    countSeries = pd.Series(count)
    selected_scriptwriters = countSeries[countSeries > 2].index

    data['selected_scriptwriter'] = data['scriptwriter'].map(lambda each: list( set(each) & set(selected_scriptwriters) ))

    onehot = mlb.fit_transform(data['selected_scriptwriter'])
    columns = mlb.classes_
    selected_scriptwriter_onehot = pd.DataFrame(onehot, columns = columns, index = data.index) #############

    reviews_json = {}
    filepaths = ['../coco_reviews.json', '../eigacom_review.json']

    for each in data.index:
        reviews_json[str(each)] = []

    temp_json = {}
    for each in filepaths:
        with open(each, 'r', encoding= 'utf-8') as f:
            temp_json[each] = json.load(f)

    for each in data.index:
        for file in filepaths:
            reviews_json[str(each)].extend(temp_json[file][str(each)]['reviews'])

    for each in data.index:
        [temp_json[file][str(each)] for file in filepaths]


    reviews = [
        pd.DataFrame(
            reviews_json[str(i)],
            columns = ['date', 'review','rating','star'] if len(reviews_json[str(i)]) == 0 else None
        ) for i in data.index
    ]

    for each in reviews:
        each['date'] = pd.to_datetime(each['date'])

    review_dataframe = pd.DataFrame(reviews, columns = ['reviews'], index = data.index)


    data.to_pickle('data.pkl')
    nomination_onehot.to_pickle('nomination_onehot.pkl')
    selected_performers_onehot.to_pickle('selected_performers_onehot.pkl')
    selected_directors_onehot.to_pickle('selected_directors_onehot.pkl')
    selected_studio_onehot.to_pickle('selected_studio_onehot.pkl')
    selected_scriptwriter_onehot.to_pickle('selected_scriptwriter_onehot.pkl')
    review_dataframe.to_pickle('review_dataframe.pkl')


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('disignate year')
        sys.exit(0)
    if len(args) == 2:
        json2dataframe(args[1])
