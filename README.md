# japanese_movies_dataset


## Usage
### メタデータの取得
[FIXME]
japanese_movies_dataset/nay/scrape_nominate_movie.py の実行

### 他の映画賞受賞データの取得
`cd japanese_movies_dataset`

最新(2020)年度のデータのみの追加は `japanese_movies_dataset/neo_review/data/nominate_movie_meta_data.json` に直接手動で入力する

`python other_nominate/join_meta_data.py --original neo_review/data/nominate_movie_meta_data.json --data neo_review/data/nominate_movie_meta_data.json --summary other_nominate/annual_other_nominate_data.json`

