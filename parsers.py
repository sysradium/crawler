from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin



class Page:
    def __init__(self, url):
        self.url = url
        self.links, self.assets = set(), set()

    def __str__(self):
        links = '\n '.join(self.links) or 'N/A'
        assets = '\n '.join(self.assets) or 'N/A'
        return 'Page {}:\nLinks:\n {}\nAssets:\n {}'.format(self.url, links, assets)


class DefaultParser:
    @staticmethod
    def extract_urls(html):
        soup = BeautifulSoup(html, 'html5lib')
        return {t.attrs['href'] for t in soup.find_all('a')}

    @staticmethod
    def extract_static_assets(html):
        soup = BeautifulSoup(html, 'html5lib')
        css = {t.attrs['href'] for t in soup.find_all('link', rel='stylesheet')}
        js = {t.attrs['src'] for t in soup.find_all('script') if 'src' in t.attrs}

        return css | js

    def parse(self, url, html):
        page = Page(url)
        urls = {self.normalize_url(url, u) for u in self.extract_urls(html)}
        static = self.extract_static_assets(html)

        page.links |= {u for u in urls if not self.is_external_url(url, u)}
        page.assets |= static

        return page

    def normalize_url(self, base_url, url):
        """
        Makes an absolute URL. If a relative path is given it's concatinated with the base url.
        Otherwise the given url is just returned
        """
        joined_url = urljoin(base_url, url)
        o = urlparse(joined_url)
        return o.scheme + "://" + o.netloc + o.path

    def is_external_url(self, entrypoint, url):
        external_url = urlparse(url).hostname
        main_url = urlparse(entrypoint).hostname

        return external_url != main_url
