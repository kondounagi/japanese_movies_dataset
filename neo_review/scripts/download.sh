#!/bin/sh
python ./coco.py \
    ../data/nominate_movie_meta_data.json \
    ../data/coco \
    $(seq 1978 $(date +%Y))

python ./merge.py ../data/nominate_movie_meta_data.json ../data/coco ../data/coco_reviews.json
rm -rf ../data/coco
