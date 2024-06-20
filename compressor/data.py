from dataclasses import dataclass
from dataclasses import fields
import os
import pandas as pd


@dataclass
class Paper:
    title: str
    authors: list | None = None
    url: str = ""
    abstract: str = ""
    full_text: str = ""
    keywords: list | None = None
    pdf_url: str = ""
    abstract_compressed: str = ""
    full_text_compressed: str = ""
    date_published: str = ""  # yyyy-mm-dd
    source: str = ""  # e.g. arxiv


class PaperDB:
    def __init__(self, fpath: str = "papers.parquet"):
        self._fpath = fpath
        if os.path.exists(fpath):
            self._df = pd.read_parquet(fpath)
        else:
            print(f"There is no database in {fpath}, creating a new one.")
            self._df = pd.DataFrame(columns=[el.name for el in fields(Paper)])
            self.commit()

    def commit(self):
        self._df.to_parquet(self._fpath)

    def purge(self):
        self._df = pd.DataFrame(columns=[el.name for el in fields(Paper)])
        self.commit()

    def add(self, paper: Paper):
        self._df.loc[len(self._df)] = [getattr(paper, f.name) for f in fields(Paper)]

    def get_papers_for_date(self, date: str):
        return self._df.loc[self._df.date_published == date]

    def get_papers_for_source(self, source: str):
        return self._df.loc[self._df.source == source]

    def add_abstract_compression(self, id: int, summary: str):
        self._df.loc[id].abstract_compressed = summary
