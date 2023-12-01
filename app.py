"""Main entry point for the compressor."""
import argparse
from compressor import crawlers
from compressor import compressors
from compressor import models
from compressor import reporters

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
        paper_abstract = crawlers.get_arxiv_paper_by_url(args.url)["summary"]
        compression_result = c_model.go(paper_abstract)
        print(compression_result)
    elif args.task == "nature-url":
        if not args.url:
            raise ValueError("You need to provide the Nature URL to summarise.")
        paper_abstract = crawlers.get_nature_paper_by_url(args.url)
        compression_result = c_model.go(paper_abstract)
        print(compression_result)
    elif args.task == "daily-arxiv":
        crawlers.crawl_arxiv()
        c = compressors.ArxivCompressor(c_model)
        c.compress()
        reporters.arxiv_daily_with_report()
    else:
        raise ValueError("Unknown task.")
