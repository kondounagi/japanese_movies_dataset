#!/bin/sh
(python ./coco.py ../$1_movie_clean $1 1 49; echo 1) &
(python ./coco.py ../$1_movie_clean $1 50 99; echo 50) &
(python ./coco.py ../$1_movie_clean $1 100 149; echo 100) &
(python ./coco.py ../$1_movie_clean $1 150 199; echo 150) &
(python ./coco.py ../$1_movie_clean $1 200 249; echo 200) &
(python ./coco.py ../$1_movie_clean $1 250 299; echo 250) &
(python ./coco.py ../$1_movie_clean $1 300 349; echo 300) &
(python ./coco.py ../$1_movie_clean $1 350 399; echo 350) &
(python ./coco.py ../$1_movie_clean $1 400 449; echo 400) &
(python ./coco.py ../$1_movie_clean $1 450 499; echo 450) &
(python ./coco.py ../$1_movie_clean $1 500 549; echo 500) &
(python ./coco.py ../$1_movie_clean $1 550 599; echo 550) &
(python ./coco.py ../$1_movie_clean $1 600 649; echo 600) &
(python ./coco.py ../$1_movie_clean $1 650 699; echo 650) &
(python ./coco.py ../$1_movie_clean $1 700 749; echo 700) &
(python ./coco.py ../$1_movie_clean $1 750 799; echo 750) &
(python ./coco.py ../$1_movie_clean $1 800 849; echo 800) &
(python ./coco.py ../$1_movie_clean $1 850 899; echo 850) &
(python ./coco.py ../$1_movie_clean $1 900 949; echo 900) &
(python ./coco.py ../$1_movie_clean $1 950 999; echo 950) &
(python ./coco.py ../$1_movie_clean $1 1000; echo 1000) &