import re
import requests
import unicodedata
from abc import abstractmethod
from bs4 import BeautifulSoup
from nay.decorators import sort_by
from nay.scraper import Scraper, Scrapable


class PrizeSet:
    def __init__(self):
        self._scraper = Scraper()

    @sort_by(lambda ds: (ds['year'], ds['name']))
    def data_set(self):
        # FIXME: Dangerous iterating over dynamic subclasses
        # TODO: ds structure is different from the original
        #       See other_nominate_data.json
        self._prefetch()

        for cls in Prize.__subclasses__():
            yield from cls().data_set()

    def _prefetch(self):
        objects = [cls() for cls in Prize.__subclasses__()]
        self._scraper.get(objects)


class Prize(Scrapable):
    def __init__(self):
        self._content = None

    @abstractmethod
    def data_set(self):
        pass

    @property
    def name(self):
        name = type(self).__name__
        return re.sub(r'(?!^)([A-Z]+)', r'_\1', name).lower()

    @property
    def content(self):
        if self._content:
            return self._content

        page = requests.get(self.url)
        self.set_content(page.content)
        return self._content

    @property
    def soup(self):
        return BeautifulSoup(self.content, 'lxml')

    def set_content(self, content):
        self._content = content

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
                    'name': self.name,
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
                    'name': self.name,
                    'year': int(match.group(1)),
                    'title': title_text,
                }


class HochiEigashou(Prize):
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
                'name': self.name,
                'year': int(self._uni_nfkc(year_elm.text)),
                'title': self._uni_nfkc(title_elm.text),
            }

        # XXX: has not yet been uploaded
        yield {
            'name': self.name,
            'year': 2018,
            'title': '孤狼の血',
        }


class MainichiFilmAward(Prize):
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
                    'name': self.name,
                    'year': int(match.group(1)),
                    'title': match.group(2),
                }


class BlueRibbonAward(Prize):
    @property
    def url(self):
        return "https://mihocinema.com/blueribbon-list"

    @sort_by(lambda ds: ds['year'])
    def data_set(self):
        for tr in self.soup.select('table tr'):
            year_elm = tr.select_one('td:nth-child(2)')
            if not year_elm:
                continue

            title_elm = tr.select_one('td:nth-child(3)')
            if not title_elm:
                continue

            year_text = self._uni_nfkc(year_elm.text)
            title_text = self._uni_nfkc(title_elm.text)

            match = re.match(r'(\d{4})年', year_text)
            if match:
                yield {
                    'name': self.name,
                    'year': int(match.group(1)),
                    'title': title_text,
                }


class KinejunBestTen(Prize):
    @property
    def url(self):
        return "http://www.kinenote.com/main/award/kinejun/"

    @sort_by(lambda ds: ds['year'])
    def data_set(self):
        for tr in self.soup.select('table.tbl_year > tr'):
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
                    'name': self.name,
                    'year': int(match.group(1)),
                    'title': title_text,
                }
