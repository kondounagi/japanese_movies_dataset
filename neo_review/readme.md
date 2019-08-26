# NAY

NAY is a project for predicting next year best prize based on previous years.

## Usage

``` bash
cd data
python3 scrape_nominate_movie.py
```

## Code Explanation

### Scraping 

Based on IDs in data/nominate_id/${year}.txt, movie metadata are scraped in data/nominate_movie_meta_data.json from eiga.com.

IDs from 1978 to 2019 have been checked intact. When data for 2020 are announced, please replace IDs in 2020.txt.

Example:
Search 天気の子 on eiga.com and its link is https://eiga.com/movie/90444/.
Then ID for this movie is 90444 and append it in 2020.txt.

### Other Nominate 

### Data Transformation

### Model Training

### ...

