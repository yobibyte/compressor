"""Main entry point for the compressor."""
import argparse
from datetime import datetime, timedelta

from compressor import compressors, crawlers, models, reporters
from compressor.data import PaperDB
import pypdf

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
            "pdf",
            "openreview",
        ],
    )
    parser.add_argument(
        "-u",
        "--url",
        default="",
        help="URL to summarise. Active if task is arxiv-url.",
    )
    parser.add_argument(
        "-v",
        "--venue",
        default="",
        help="Venue to summarise. Active if task is openreview.",
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
    elif args.task == "openreview":
        venue = args.venue
        venue = "ICLR.cc/2024/Conference"
        #crawlers.crawl_openreview("iclr2024.csv", venue)
        c = compressors.Compressor(source=venue, model=c_model)
        c.compress()
    elif args.task == "pdf":
        # TODO: We are very generous with the text inputs here. Glue the broken words.
        # Get rid of junk. Sanitize.
        # TODO: Currently we crop the paper to avoid memory blow up. Come up with a way to summarise the whole thing locally.
        doc = pypdf.PdfReader(args.url)
        fulltext = "\n".join([p.extract_text() for p in doc.pages])
        compression_result = c_model.go(fulltext, full_summary=True)
        print(compression_result)
    else:
        raise ValueError("Unknown task.")
