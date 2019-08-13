import sys
import csv
import glob
import os


year = int(sys.argv[1])
try:
    os.mkdir('./jsons/{}'.format(year))
except:
    pass

with open('../{}_movie_clean'.format(year), 'r') as f:
    dataReader = csv.reader(f, delimiter='\t')
    for row in dataReader:
        movie_id = row[0]
        title = row[1]
        # print(movie_id, title)
        print('./jsons/metadata/{}/{}.json'.format(year, title))
        try:
            os.rename(
                './jsons/metadata/{}/{}.json'.format(year, title),
                './jsons/{}/{}.json'.format(year, movie_id)
            )
        except Exception as e:
            print(e)
            # pass
