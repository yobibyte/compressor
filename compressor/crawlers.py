import urllib
import urllib.request
from tqdm import tqdm
import feedparser
from datetime import datetime, timedelta
from compressor.data import Paper
from compressor.data import PaperDB
import openreview
from bs4 import BeautifulSoup
from getpass import getpass
import os

CATEGORIES_OF_INTEREST = {"cs.LG", "cs.AI", "cs.CV", "cs.CL"}
PAGE_SIZE = 100
# TODO add support for multiple dates. Probably keep the last date of submission and get everything up until now.
DESIRED_DATE = datetime.now() - timedelta(1)

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
]


def get_nature_paper_by_url(url: str) -> str:
    id = url.split("/")[-1].strip("/")
    url = f"https://www.nature.com/articles/{id}"
    data = urllib.request.urlopen(url)
    soup = BeautifulSoup(
        data.read().decode("utf-8"),
        "html.parser",
    )
    abstract_content = soup.find(
        "div",
        attrs={"id": "Abs1-content"},
    )
    return abstract_content.get_text()


def get_arxiv_paper_by_url(url: str):
    id = url.split("/")[-1].strip("/")
    url = f"http://export.arxiv.org/api/query?search_query=id:{id}&sortBy=submittedDate&sortOrder=descending&max_results=1"
    data = urllib.request.urlopen(url)
    results = data.read().decode("utf-8")
    return feedparser.parse(results).entries[0]


def api_call(start=0, max_results=100):
    cat_condition = f"cat:{'+OR+'.join(CATEGORIES_OF_INTEREST)}"
    url = f"http://export.arxiv.org/api/query?search_query={cat_condition}&start={start}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    data = urllib.request.urlopen(url)
    results = data.read().decode("utf-8")
    return feedparser.parse(results)


def crawl_arxiv(db: PaperDB | None = None):
    ctr = 0
    # Arxiv does not track the announcement date.
    # This is the date the paper was submitted.
    ty, tm, td = DESIRED_DATE.strftime("%Y-%m-%d").split("-")
    print(ty, tm, td)
    stop_parsing = False
    if not db:
        db = PaperDB()
    while True:
        results = api_call(ctr, PAGE_SIZE)
        for el in results["entries"]:
            entry_date = datetime.fromisoformat(el["published"].rstrip("Z")).strftime(
                "%Y-%m-%d"
            )
            ey, em, ed = entry_date.split("-")
            if ty == ey and tm == em and td == ed:
                if el["arxiv_primary_category"]["term"] in CATEGORIES_OF_INTEREST:
                    paper = Paper(
                        title=el["title"].replace("\n", ""),
                        abstract=el["summary"].replace("\n", " "),
                        url=el["link"],
                        authors=",".join([a["name"] for a in el["authors"]]),
                        date_published=entry_date,
                        source="arxiv",
                    )
                    casefold_summary = paper.abstract.casefold()
                    if not any([kw in casefold_summary for kw in keywords_to_skip]):
                        if paper.url not in db._df.url.values:
                            db.add(paper)
            else:
                stop_parsing = True
                break
        print(f"Parsing in progress...")
        if stop_parsing:
            break
        ctr += PAGE_SIZE

    valid_entries = db.get_papers_for_date(f"{ty}-{tm}-{td}")
    print(f"Found {len(valid_entries)} papers.")
    if len(valid_entries) > 0:
        db.commit()


def crawl_openreview(output_fname: str, venue_id: str):
    username = input("Enter your OpenReview email.")
    password = getpass()
    client = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net", username=username, password=password
    )
    submissions = client.get_all_notes(content={"venueid": venue_id})
    processed_urls = set()
    if os.path.exists(output_fname):
        with open(output_fname, "r") as f:
            for el in f:
                processed_urls.add(el.split("|")[2])

    db = PaperDB()
    for s in tqdm(submissions):
        paper = Paper(
            title=s.content["title"]["value"],
            url=f"https://openreview.net/forum?id={s.forum}",
            abstract=s.content["abstract"]["value"],
            authors=", ".join(s.content["authors"]["value"]),
            keywords=", ".join(s.content["keywords"]["value"]),
            source=venue_id,
        )
        db.add(paper)
        db.commit()


if __name__ == "__main__":
    paper = get_nature_paper_by_url(
        "https://www.nature.com/articles/s41586-023-06735-9"
    )
