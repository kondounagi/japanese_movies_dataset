#!/bin/sh
python ./coco.py \
    ../data/nominate_movie_meta_data.json \
    ../data/coco \
    $(seq 1978 2020)

python ./mearge.py ../data/nominate_movie_meta_data.json ../data/coco ../data/coco_reviews.json
rm -rf ../data/coco
