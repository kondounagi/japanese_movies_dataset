import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from nay.decorators import sort_by


class Prize:
    def __init__(self):
        self._soup = None

    def data_set(self):
        return [cls.__name__ for cls in type(self).__subclasses__()]

    @property
    def url(self):
        raise NotImplementedError

    @property
    def soup(self):
        if self._soup is not None:
            return self._soup

        page = requests.get(self.url)
        self._soup = BeautifulSoup(page.content, 'lxml')
        return self._soup

    @staticmethod
    def _uni_nfkc(text):
        return unicodedata.normalize('NFKC', text)


class NikkanSports(Prize):
    @property
    def url(self):
        return "https://www.nikkansports.com/entertainment/award/ns-cinema/history/"  # noqa: E501

    @sort_by(lambda ds: ds['year'], uniq=True)
    def data_set(self):
        for table in self.soup.select('table.nsTable'):
            year_text = self._uni_nfkc(table.select_one('caption').text)
            title_text = self._uni_nfkc(table.select_one('tr > td').text)

            match = re.match(r'第\d+回\((\d{4})年\)', year_text)
            if match:
                yield {
                    'year': int(match.group(1)),
                    'title': title_text,
                }


class GoldenGross(Prize):
    @property
    def url(self):
        return "https://ja.wikipedia.org/wiki/ゴールデングロス賞"

    @sort_by(lambda ds: ds['year'])
    def data_set(self):
        for tr in self.soup.select('table.wikitable > tbody > tr'):
            year_elm = tr.select_one('td:nth-child(1) > a')
            if not year_elm:
                continue

            title_elm = tr.select_one('td:nth-child(3) > a')
            if not title_elm:
                continue

            year_text = self._uni_nfkc(year_elm.text)
            title_text = self._uni_nfkc(title_elm.text)

            match = re.match(r'(\d{4})年', year_text)
            if match:
                yield {
                    'year': int(match.group(1)),
                    'title': title_text,
                }


class HochiEiga(Prize):
    @property
    def url(self):
        return "https://www.hochi.co.jp/award/hochi_eigashou/history.html"

    @sort_by(lambda ds: ds['year'], uniq=True)
    def data_set(self):
        for tr in self.soup.select('table.btable > tr'):
            year_elm = tr.select_one('td:nth-child(2)')
            if not year_elm:
                continue

            title_elm = tr.select_one('td:nth-child(3)')
            if not title_elm:
                continue

            yield {
                'year': int(self._uni_nfkc(year_elm.text)),
                'title': self._uni_nfkc(title_elm.text),
            }

        # XXX: has not yet been uploaded
        yield {
            'year': 2018,
            'title': '孤狼の血',
        }


class MainichiFilm(Prize):
    @property
    def url(self):
        return "https://mainichi.jp/mfa/history/"

    @sort_by(lambda ds: ds['year'])
    def data_set(self):
        for li in self.soup.select("ul.list-history > li"):
            line = self._uni_nfkc(li.select_one('a').text)

            match = re.match(r'(\d{4})年\(第\d+回\)『(.*)』', line)
            if match:
                yield {
                    'year': int(match.group(1)),
                    'title': match.group(2),
                }


class BlueRibbon(Prize):
    @property
    def url(self):
        return "http://www.allcinema.net/prog/award_top.php?num_a=41"

    @sort_by(lambda ds: ds['year'])
    def data_set(self):
        for tr in self.soup.select('tr.c2'):
            year_text = self._uni_nfkc(
                tr.select_one('td:nth-child(1) > a').text)
            title_text = self._uni_nfkc(
                tr.select_one('td:nth-child(3) > a').text)

            match = re.match(r'(\d{4})年', year_text)
            if match:
                yield {
                    'year': int(match.group(1)),
                    'title': title_text,
                }
