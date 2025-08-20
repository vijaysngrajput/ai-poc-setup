import os
import glob
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json
from tqdm import tqdm
from config import DATA_DIR, INDEX_DIR, EMBEDDING_MODEL, HF_CACHE
from utils import row_to_text, normalize, save_faiss

os.environ["HF_HOME"] = HF_CACHE
os.environ["TRANSFORMERS_CACHE"] = HF_CACHE

def main():
    files = glob.glob(os.path.join(DATA_DIR, '*.xlsx'))
    model = SentenceTransformer(EMBEDDING_MODEL)
    meta = []
    vectors = []
    counts = {}
    idx = 0
    for file in files:
        fname = os.path.basename(file)
        xls = pd.ExcelFile(file)
        for sheet in xls.sheet_names:
            df = xls.parse(sheet)
            df = df.dropna(how='all')
            counts.setdefault(fname, {})[sheet] = 0
            for i, row in df.iterrows():
                text = row_to_text(row, fname, sheet)
                if not text.strip():
                    continue
                meta.append({"id": idx, "file": fname, "sheet": sheet, "row_idx": int(i), "text": text})
                vectors.append(text)
                counts[fname][sheet] += 1
                idx += 1
    print(f"Loaded {len(vectors)} rows from {len(files)} files.")
    if not vectors:
        print("No data found. Exiting.")
        return
    embeds = model.encode(vectors, show_progress_bar=True, batch_size=64)
    embeds = normalize(embeds)
    index = faiss.IndexFlatIP(embeds.shape[1])
    index.add(embeds.astype(np.float32))
    os.makedirs(INDEX_DIR, exist_ok=True)
    save_faiss(index, meta, INDEX_DIR)
    print("Index built and saved.")
    print("Counts per file/sheet:")
    for f, sheets in counts.items():
        for s, c in sheets.items():
            print(f"  {f} [{s}]: {c} rows")
    print(f"Total vectors: {len(vectors)}")

if __name__ == "__main__":
    main()
