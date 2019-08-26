Japanese Movie Awards exclude Academy
====
アカデミー賞以外の日本の映画賞データの取得

## Description
(全体のREADME.mdに統合するかもしれません)

日刊スポーツ映画大賞、ゴールデングロス賞、報知映画賞、毎日映画コンクール、
ブルーリボン賞、キネマ旬報ベストテンを受賞した映画のデータを取得する

## Requirement
* python 3.6.0

* requests
* html
* selenium

## Usage
### 複数年のデータを取得する場合
`dump_other_nominate.py`の対象年度を書き換える
```python
self.years = range(2003, 2019)
```
その後、実行

`python dump_other_nominate.py`


### 単年(特に最新年)のデータを取得する場合

最新年度のデータは他のデータと形式が違うことが多く、自動化できないため
_other_nominate/annual_other_nominate_data.json_ に `index` 以外のデータを手入力する

もしくは、ここのコードを使わずに `neo_review/data/nominate_movie_meta_data.json` に直接手動で入力（推奨）


### メタデータとの統合
必要に応じて対象年度を書き換える

`python join_meta_data.py`


## Install
git clone https://github.com/kondounagi/japanese_movies_dataset/

cd japanese_movies_dataset/other_nominate/
