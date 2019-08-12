#!/usr/bin/env python3
import re
import sys
import unicodedata

year = int(sys.argv[1])

def main():
    month = 0
    day = 0

    re_month = re.compile('^([0-9]+)月$')
    re_day = re.compile('^([0-9]+)日$')
    re_image_desc = re.compile(r'\s*[(（][^)）]*の旗[^)）]*[)）]')
    re_trailing_num = re.compile(r'(?:\s*\[[0-9]+\])+$')
    re_garbage = re.compile(r'\s*[(（][^)）]*$')

    num = 0
    with open(str(year) + "_movie_raw", "r") as in_file:
        for line in in_file:
            line = line.strip()

            match_month = re_month.match(line)
            match_day = re_day.match(line)

            if match_month:
                month = match_month.group(1)
                continue

            if match_day:
                day = match_day.group(1)
                continue

            # FIXME: Regexp can't handle nested parens, need stack parser
            line = re_image_desc.sub('', line)

            line = re_trailing_num.sub('', line)
            line = re_garbage.sub('', line)

            line = unicodedata.normalize('NFC', line)

            num += 1
            print(num, line, str(year), month, day, sep='\t')


if __name__ == '__main__':
    main()
