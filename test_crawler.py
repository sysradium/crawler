import aiohttp
import asyncio
import crawler as cr
import pytest
from aioresponses import aioresponses


@pytest.fixture
def url():
    return 'http://localhost'


@pytest.fixture
def crawler(event_loop, url):
    with cr.Crawler(url, loop=event_loop) as crawler:
        yield crawler


def test_smoke(crawler):
    pass


def test_on_initial_empty_page_crawler_gathers_just_one_page(url):
    loop = asyncio.get_event_loop()
    with aioresponses() as m:
        with cr.Crawler(url, loop=loop) as crawler:
            m.get(url, body='lalala', status=200, headers={'Content-Type': 'text/html'})
            m.get(url, body='lalala', status=200, headers={'Content-Type': 'text/html'})
            loop.run_until_complete(crawler.crawl())
            assert len(crawler.fetched_pages) == 1
