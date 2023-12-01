"""Main entry point for the compressor."""
import argparse
import crawler
import compressor
import model
import reporter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Compressor", description="Compress the internet"
    )
    parser.add_argument(
        "-m", "--model", default="orca", choices=model.MODEL_MENU.keys()
    )
    parser.add_argument(
        "-t", "--task", default="arxiv-url", choices=["arxiv-url", "daily-arxiv"]
    )
    parser.add_argument(
        "-u",
        "--url",
        default="",
        help="Arxiv URL to summarise. Active if task is arxiv-url.",
    )
    args = parser.parse_args()

    c_model = model.MODEL_MENU[args.model]()

    if args.task == "arxiv-url":
        # Add option to summarise full papers.
        if not args.url:
            raise ValueError("You need to provide the Arxiv URL to summarise.")
        paper_abstract = crawler.get_arxiv_paper_by_url(args.url)["summary"]
        compression_result = c_model.go(paper_abstract)
        print(compression_result)
    if args.task == "daily-arxiv":
        crawler.crawl_arxiv()
        c = compressor.ArxivCompressor(c_model)
        c.compress()
        reporter.arxiv_daily_with_report()
