from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from scraper import urlFullText, subDomains, numOfTokenPerURL, urls, numOfUniqueUrls, longestPage, addFreqDist



class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)

        print(numOfUniqueUrls(urls))
        print(longestPage())
        print(addFreqDist(urlFullText))
        print(len(subDomains))

        with open("output.txt", "w+") as report:
            report.write("Number of Unique URLS: " + str(numOfUniqueUrls(urls)) + '\n' + '\n')
            report.write("Longest page found: " + str(longestPage()) + '\n' + '\n')

            for i in addFreqDist(urlFullText):
                report.write(f'{i[0]} found {i[1]} times \n')
            for i in subDomains.items():
                report.write(f'{i[0]} has {i[1]} unique pages \n')
            


