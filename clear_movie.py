import re
import unicodedata
import sys

def main():
    year = 2018
    month = 0
    day = 0

    re_month = re.compile('^([0-9]+)月$')
    re_day = re.compile('^([0-9]+)日$')

    with open("2018_movie_raw", "r") as in_file:
        for line in in_file.readlines():
            line = line.strip()

            match_month = re_month.match(line)
            match_day = re_day.match(line)

            if match_month:
                month = match_month.group(1)
                continue

            if match_day:
                day = match_day.group(1)
                continue

            end = len(line)
            for i in range(len(line)):

                if (line[len(line) - i - 1] == '(' or line[len(line) - 1 - i] == '（'):
                    end = len(line) - i - 1
                    break

            line = line[0:end].strip()
            line = unicodedata.normalize('NFC', line)
            print(line, year, month, day, sep='\t')


if __name__ == '__main__':
    main()
