import exceptions as exp
import logging
import parsers
from urllib.parse import urljoin

import aiohttp
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Crawler:
    def __init__(self, entrypoint, loop, workers_num=100, parser=None, session=None):
        self.entrypoint = entrypoint
        self.seen_urls = set()
        self.fetched_pages = []
        self.queue = asyncio.queues.Queue()
        self.workers_num = workers_num
        self.loop = loop

        if session is None:
            self.session = aiohttp.ClientSession(loop=loop)
        else:
            self.session = session

        if parser is None:
            self.parser = parsers.DefaultParser()
        else:
            self.parser = parser

    async def _probe_url(self, url):
        """
        Probes the given URL and returns the URL it was redirected to
        """
        async with self.session.get(url) as response:
            response.raise_for_status()
            return response.url

    async def fetch(self, url):
        """
        Given a URL fetches the HTML from the URL and returns it
        """
        async with self.session.get(url) as response:
            response.raise_for_status()

            if response.content_type not in ['text/plain', 'text/html']:
                raise exp.UnsupportedResponseType(response.content_type)

            data = await response.text()
            return data

    async def worker(self, i):
        """
        Represent a worker (consumer) of URLs. It runs "forever" and waits for the URL from the queue. This worker
        couroutine should be terminated outside
        """
        while True:
            url = await self.queue.get()

            try:
                page = await self.process_url(url)
                self.seen_urls.add(url)
                self.fetched_pages.append(page)

                unseen_urls = set(page.links) - self.seen_urls
                for t in unseen_urls:
                    self.queue.put_nowait(t)

            except exp.GenericCrawlerException:
                logger.error('Got unsupported response from {}, skipping'.format(url))
                self.seen_urls.add(url)
            except aiohttp.errors.HttpProcessingError as e:
                # If the resource was not found - give up
                if e.code == 404:
                    raise
                self.queue.put_nowait(url)
            finally:
                self.queue.task_done()

        logger.debug('Worker {} done'.format(i))

    async def process_url(self, url):
        html = await self.fetch(url)
        page = self.parser.parse(url, html)
        return page

    async def crawl(self):
        """
        Lauches workers and starts crawling over the URLs until the queue of unvisited URLs becomes empty
        """
        await self.queue.put(await self._probe_url(self.entrypoint))

        workers = [
            asyncio.ensure_future(self.worker(i)) for i in range(self.workers_num)
        ]

        logger.debug('Joined on queue')
        await self.queue.join()

        logger.debug('Queue empty')
        for c in workers:
            c.cancel()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
