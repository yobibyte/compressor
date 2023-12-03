"""Main entry point for the compressor."""
import argparse
from datetime import datetime, timedelta

from compressor import compressors, crawlers, models, reporters
from compressor.data import PaperDB

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Compressor", description="Compress the internet"
    )
    parser.add_argument(
        "-m", "--model", default="orca", choices=models.MODEL_MENU.keys()
    )
    parser.add_argument(
        "-t",
        "--task",
        default="arxiv-url",
        choices=[
            "arxiv-url",
            "daily-arxiv",
            "nature-url",
        ],
    )
    parser.add_argument(
        "-u",
        "--url",
        default="",
        help="Arxiv URL to summarise. Active if task is arxiv-url.",
    )
    args = parser.parse_args()

    c_model = models.MODEL_MENU[args.model]()

    if args.task == "arxiv-url":
        # Add option to summarise full papers.
        if not args.url:
            raise ValueError("You need to provide the Arxiv URL to summarise.")
        paper_abstract = crawlers.ArxivCrawler().get_abstract(args.url)
        compression_result = c_model.go(paper_abstract)
        print(compression_result)
    elif args.task == "nature-url":
        if not args.url:
            raise ValueError("You need to provide the Nature URL to summarise.")
        paper_abstract = crawlers.NatureCrawler().get_abstract(args.url)
        compression_result = c_model.go(paper_abstract)
        print(compression_result)
    elif args.task == "daily-arxiv":
        # If there are several days between submission and announcement,
        # crawl all these days.
        arxiv_df = PaperDB().get_papers_for_source("arxiv")
        if len(arxiv_df) > 0:
            oldest_date = max(arxiv_df.date_published.values)
            oldest_date = datetime.strptime(oldest_date, "%Y-%m-%d") + timedelta(days=1)
        else:
            oldest_date = None
        crawlers.crawl_arxiv(oldest_date=oldest_date)
        c = compressors.ArxivCompressor(c_model)
        c.compress()
        reporters.arxiv_daily_with_report()
    else:
        raise ValueError("Unknown task.")
