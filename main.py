import logging
import sys

import asyncio
import crawler

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':

    try:
        url = sys.argv[1]
    except KeyError:
        print('Please enter the URL to start crawling from')
        sys.exit(1)

    loop = asyncio.get_event_loop()
    try:
        with crawler.Crawler(url, loop=loop, workers_num=1000) as crawler:
            loop.run_until_complete(crawler.crawl())
            for page in crawler.fetched_pages:
                print(10 * '=')
                print(page)
    except KeyboardInterrupt:
        pass
