from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .crawler import Crawler
from .helpers import has_class


class AsciiDoc(Crawler):
    def crawl(self, library_key: str) -> dict:
        sections = {}
        index_path = self._boost_root / 'libs' / library_key / 'index.html'

        # resolve redirect address
        with open(index_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            assert soup.select_one('head > meta[http-equiv="refresh"]')
            redirect_to = soup.select_one('body a').get("href")
            index_path = urljoin(str(index_path), redirect_to)

        with open(index_path, 'r', encoding='utf-8', errors='ignore') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            for sect1 in soup.select('body > div[id="content"] > .sect1'):
                self._extract_section_n(index_path, sections, sect1)

        return sections

    def _extract_section_n(self, index_path: str, sections: dict, sect: Tag, lvls: list = []):
        header = sect.select_one('h1, h2, h3, h4, h5, h6')
        lvls = lvls + [header.text]

        if header.find_next_sibling() and has_class(header.find_next_sibling(), 'sectionbody'):
            siblings = header.find_next_sibling().find_all(recursive=False)
        else:
            siblings = header.find_next_siblings()

        content = ''
        for sibling in siblings:
            if sibling.has_attr('class') and len([i for i in sibling.get('class') if i.startswith('sect')]) > 0:
                self._extract_section_n(index_path, sections, sibling, lvls)
                continue
            content += sibling.get_text() + ' '

        sections[index_path + '#' + header.get('id')] = {'content': content, 'lvls': lvls}
