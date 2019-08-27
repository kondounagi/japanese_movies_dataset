# japanese_movies_dataset


## Usage
### メタデータの取得
#### Usage
```bash
cd neo_review/data
python scrape_nominate_movie.py
```

#### How to update new data
Based on IDs in data/nominate_id/${year}.txt, movie metadata are scraped in data/nominate_movie_meta_data.json from eiga.com.

IDs from 1978 to 2019 have been checked intact. When data for 2020 are announced, please replace IDs in 2020.txt.

Example:
Search 天気の子 on eiga.com and its link is https://eiga.com/movie/90444/.
Then ID for this movie is 90444 and append it in 2020.txt.

### 他の映画賞受賞データの取得
`cd japanese_movies_dataset`

最新(2020)年度のデータのみの追加は `japanese_movies_dataset/neo_review/data/nominate_movie_meta_data.json` に直接手動で入力する

#### `nominate_movie_meta_data.json` のデータ説明

    {
        "YYYY(年度)": [
            {
                "director(監督)": [<str>,...],
                "scriptwriter(脚本)": [<str>,...],
                "performers(出演者)": [<str>,...],
                "screen_time(上映時間/分)": <int>,
                "production_studio(配給元)": <str>,
                "title(題名)": <str>,
                "year(公開年)": <str>,
                "month(公開月)": <str>,
                "day(公開日)": <str>,
                "id": <int>,                           # FIXME: どこから？
                "other_nominates": [
                    {
                        "award": "nikkan_sports",
                        "prized(受賞)": int(<bool>)
                    },
                    {
                        "award": "golden_gross",
                        "prized(受賞)": int(<bool>)
                    },
                    {
                        "award": "hochi_eigashou",
                        "prized(受賞)": int(<bool>)
                    },
                    {
                        "award": "mainichi_film_award",
                        "prized(受賞)": int(<bool>)
                    },
                    {
                        "award": "blue_ribbon_award",
                        "prized(受賞)": int(<bool>)
                    },
                    {
                        "award": "kinejun_best_ten",
                        "prized(受賞)": int(<bool>)
                    }
                ]
            },
            ...
        ],
        ...
    }

`python other_nominate/join_meta_data.py --original neo_review/data/nominate_movie_meta_data.json --data neo_review/data/nominate_movie_meta_data.json --summary other_nominate/annual_other_nominate_data.json`

### スクレイピングしたデータをpandasのDataframe化する

### データの正規化
```
( cd neo_review/data/dataframes; python generate_std_data.py 2020 )
```
### 予測
#### Usage
```bash
cd neo_review/scripts
python final_model_2020.py
```
#### Output
```
1 (title) (probability)
2 (title) (probability)
3 (title) (probability)
4 (title) (probability)
5 (title) (probability)
```
The first movie is predicted most likely to win the prize !
