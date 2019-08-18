import sys
import csv
import os


year = int(sys.argv[1])
os.makedirs(f'./jsons/{year}', exist_ok=True)

with open(f'../{year}_movie_clean', 'r') as f:
    data_reader = csv.reader(f, delimiter='\t')
    for movie_id, title, *_ in data_reader:
        # print(movie_id, title)
        src = f'./jsons/metadata/{year}/{title}.json'
        dst = f'./jsons/{year}/{movie_id}.json'
        print(src)
        try:
            os.rename(src, dst)
        except Exception as e:
            print(e)
            # pass
