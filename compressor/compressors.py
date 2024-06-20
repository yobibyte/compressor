from compressor.data import PaperDB
from tqdm import tqdm
from compressor import models


class Compressor:
    def __init__(
        self, source: str, model: models.CompressorModel, db: PaperDB | None = None
    ):
        self._source = source
        self._db = db if db else PaperDB()
        self._model = model

    def retrieve(self):
        return self._db.get_papers_for_source(self._source)

    def compress(self):
        df = self.retrieve()
        print(f"Compressing {len(df)} papers...")
        results = []
        for pid, paper in tqdm(df.iterrows(), total=len(df)):
            title = paper.title
            url = paper.url
            abstract = paper.abstract
            compressed_abstract = self._model.go(abstract)
            self._db.add_abstract_compression(pid, compressed_abstract)
            self._db.commit()
            results.append((title, url, compressed_abstract))


class ArxivCompressor(Compressor):
    def __init__(self, model, db: PaperDB | None = None):
        super().__init__("arxiv", model=model, db=db)

    def retrieve(self):
        df = super().retrieve()
        res = df.loc[(df.abstract_compressed.isna()) | (df.abstract_compressed == "")]
        return res
