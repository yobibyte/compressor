import os
import re
import urllib
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from getpass import getpass

import feedparser
import openreview
from bs4 import BeautifulSoup
from tqdm import tqdm

from compressor.data import Paper, PaperDB

CATEGORIES_OF_INTEREST = {"cs.LG", "cs.AI", "cs.CV", "cs.CL"}
PAGE_SIZE = 100
# TODO add support for multiple dates. Probably keep the last date of submission and get everything up until now.
# ^^^ Crawlers support the oldest date to parse now. Compressor now compresses everything that is not compressed yet. Make this work for reporter. Use oldest date as well.

keywords_to_skip = [
    "adversarial attacks",
    "blockchain",
    "emotion recognition",
    "occupancy prediction",
    "federated",
    "motion capture",
    "shape reconstruction",
    "surveillance",
    "structure prediction",
    "segmentation",
    "action recognition",
]


class AbstractCrawler(ABC):
    @abstractmethod
    def crawl(self, url: str): ...

    @abstractmethod
    def get_full_text(self, url: str) -> str: ...

    @abstractmethod
    def get_abstract(self, url: str) -> str: ...


class NatureCrawler(AbstractCrawler):
    def crawl(self, url: str):
        # TODO: return Paper class here, not response.
        # response -> Paper object is a responsibility
        # of each of the Crawler Class objects.
        id = url.split("/")[-1].strip("/")
        url = f"https://www.nature.com/articles/{id}"
        return urllib.request.urlopen(url)

    def get_abstract(self, url: str) -> str:
        data = self.crawl(url)
        soup = BeautifulSoup(
            data.read().decode("utf-8"),
            "html.parser",
        )
        abstract_content = soup.find(
            "div",
            attrs={"id": re.compile("Abs\d-content")},
        )
        return abstract_content.get_text()

    def get_full_text(self, url: str) -> str:
        raise NotImplementedError()


class ArxivCrawler(AbstractCrawler):
    def crawl(self, url: str):
        id = url.split("/")[-1].strip("/")
        url = f"http://export.arxiv.org/api/query?search_query=id:{id}&sortBy=submittedDate&sortOrder=descending&max_results=1"
        return urllib.request.urlopen(url)

    def get_abstract(self, url: str):
        data = self.crawl(url)
        results = data.read().decode("utf-8")
        return feedparser.parse(results).entries[0]["summary"]

    def get_full_text(self, url: str) -> str:
        raise NotImplementedError()


def api_call(start=0, max_results=100):
    cat_condition = f"cat:{'+OR+'.join(CATEGORIES_OF_INTEREST)}"
    url = f"http://export.arxiv.org/api/query?search_query={cat_condition}&start={start}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    data = urllib.request.urlopen(url)
    results = data.read().decode("utf-8")
    return feedparser.parse(results)


# Use ArxivCrawler here
def crawl_arxiv(db: PaperDB | None = None, oldest_date: datetime | None = None):
    """Crawl all Arxiv articles given the filters.

    Args:
        db: PaperDB object that stores our articles.
        oldest_date: datetime object that defines the oldest date we will
            crawl the articles for. This date is included.
    """
    ctr = 0
    # Arxiv does not track the announcement date.
    # This is the date the paper was submitted.

    if not db:
        db = PaperDB()
    # TODO: replace arxiv with a constant.
    if oldest_date is None:
        oldest_date = datetime.now() - timedelta(1)
    print(f"Oldest date to crawl for: {oldest_date}")
    stop_crawling = False
    while True:
        results = api_call(ctr, PAGE_SIZE)
        if not results["entries"]:
            print("No entries found... Exiting.")
            break
        for el in results["entries"]:
            entry_date = datetime.fromisoformat(el["published"].rstrip("Z"))
            if entry_date >= oldest_date:
                if el["arxiv_primary_category"]["term"] in CATEGORIES_OF_INTEREST:
                    paper = Paper(
                        title=el["title"].replace("\n", ""),
                        abstract=el["summary"].replace("\n", " "),
                        url=el["link"],
                        authors=",".join([a["name"] for a in el["authors"]]),
                        date_published=entry_date.strftime("%Y-%m-%d"),
                        source="arxiv",
                    )
                    casefold_summary = paper.abstract.casefold()
                    if not any([kw in casefold_summary for kw in keywords_to_skip]):
                        if paper.url not in db._df.url.values:
                            db.add(paper)
                            db.commit()
            else:
                # Since responses are sorted by date, as soon as we are beyond the target date,
                # we are done.
                stop_crawling = True
                break
        print(f"Crawling in progress...")
        if stop_crawling:
            break
        ctr += PAGE_SIZE


def crawl_openreview(venue_id: str):
    username = input("Enter your OpenReview email.")
    password = getpass()
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net", username=username, password=password
    )
    submissions = client.get_all_notes(content={"venueid": venue_id})

    db = PaperDB()
    for s in tqdm(submissions):
        paper = Paper(
            title=s.content["title"]["value"],
            url=f"https://openreview.net/forum?id={s.forum}",
            abstract=s.content["abstract"]["value"],
            authors=", ".join(
                s.content["authors"]["value"] if "authors" in s.content else ""
            ),
            keywords=(
                ", ".join(s.content["keywords"]["value"])
                if "keywords" in s.content
                else ""
            ),
            source=venue_id,
        )
        db.add(paper)
        db.commit()


if __name__ == "__main__":
    abstract = NatureCrawler().get_abstract(
        "https://www.nature.com/articles/s41586-023-06735-9"
    )
    print(abstract)
