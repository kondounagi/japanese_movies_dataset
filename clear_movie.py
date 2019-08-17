#!/usr/bin/env python3
import argparse
import contextlib
import os
import re
import sys
import unicodedata


def parse_arg():
    parser = argparse.ArgumentParser(description="raw2clean")
    parser.add_argument('arg',
                        help='[year|filepath]',
                        type=str)
    args = parser.parse_args()

    if not sys.stdin.isatty():
        year = int(args.arg)
        filename = None
        return year, filename

    try:
        year = int(args.arg)
        filename = "{}_movie_raw".format(args.arg)
    except ValueError:
        filename = args.arg
        basename = os.path.basename(filename)
        match = re.search(r'^\d+', basename)
        if match:
            year = int(match.group())
        else:
            raise

    return year, filename


def clean_paren(text):
    """Remove nested parentheses from text.

    >>> clean_paren( 'アンダー・ザ・ウォーター（ スウェーデン・ デンマーク・ フィンランド）')
    'アンダー・ザ・ウォーター'

    >>> clean_paren( '葡萄畑に帰ろう (ジョージア (国)の旗 ジョージア)')
    '葡萄畑に帰ろう '

    >>> clean_paren('(r)adius ラディウス（英語版）')  # OMG
    'adius ラディウス'
    """
    left_parenthese = 0
    right_parenthese = 0

    saved = []
    for char in text:
        if char == "(" or char == "（":
            left_parenthese += 1
        elif char == ")" or char == "）":
            right_parenthese += 1
        elif right_parenthese >= left_parenthese:
            saved.append(char)

    return ''.join(saved)


@contextlib.contextmanager
def open_resource(filename):
    if filename:
        fh = open(filename, 'r')
    else:
        fh = sys.stdin

    try:
        yield fh
    finally:
        if filename:
            fh.close()


def main(year, filename):
    month = 0
    day = 0

    re_month = re.compile('^([0-9]+)月$')
    re_day = re.compile('^([0-9]+)日$')
    re_trailing_num = re.compile(r'(?:\s*\[[0-9]+\])+$')

    num = 0
    with open_resource(filename) as in_file:
        for line in in_file:
            line = line.strip()

            match_month = re_month.match(line)
            if match_month:
                month = match_month.group(1)
                continue

            match_day = re_day.match(line)
            if match_day:
                day = match_day.group(1)
                continue

            line = clean_paren(line)
            line = re_trailing_num.sub('', line)

            line = unicodedata.normalize('NFC', line)

            num += 1
            print(num, line, str(year), month, day, sep='\t')


if __name__ == '__main__':
    year, filename = parse_arg()
    main(year, filename)
