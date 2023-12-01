# git clone git@github.com:openreview/openreview-py.git

from data import PaperDB
from tqdm import tqdm
import pandas as pd


def generate_html_report(
    df: pd.DataFrame, header: str, fname: str, full_text_summary: bool = False
):
    # Summarise the latest results from arxiv.
    with open(fname, "w") as f:
        f.write(header)
        for _, paper in tqdm(df.iterrows(), total=len(df)):
            title = paper.title
            url = paper.url
            if full_text_summary:
                raise ValueError("Full text summary is not yet supported. Stay tuned.")
            else:
                summary = paper.abstract_compressed
            f.write(f"<hr>")
            f.write(f"<h3>{title}</h3>\n")
            f.write(f"<p>{paper.authors}</p>\n")
            f.write(f"<p><a href='{url}'>{url}</a></p>\n")
            f.write(f"<p><b>Compressor summary</b>: {summary}</p>")

def arxiv_daily_with_report():
    db = PaperDB()
    arxiv_df = db.get_papers_for_source("arxiv")
    latest_date = max(arxiv_df.date_published.values)
    arxiv_df = arxiv_df.loc[arxiv_df.date_published == latest_date]
    print(f"Summarising for date: {latest_date}")
    header = f"""
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <link rel="stylesheet" href="../style.css"/>
            <title>COMPRESSOR!!!</title>
    """
    generate_html_report(arxiv_df, header, "report.html")

if __name__ == "__main__":
    arxiv_daily_with_report()
