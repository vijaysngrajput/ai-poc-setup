import os
import numpy as np
import faiss
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json

def load_faiss(index_dir):
    index_path = os.path.join(index_dir, 'faiss.index')
    meta_path = os.path.join(index_dir, 'meta.jsonl')
    index = faiss.read_index(index_path)
    meta = []
    with open(meta_path, 'r', encoding='utf-8') as f:
        for line in f:
            meta.append(json.loads(line))
    return index, meta

def save_faiss(index, meta, index_dir):
    index_path = os.path.join(index_dir, 'faiss.index')
    meta_path = os.path.join(index_dir, 'meta.jsonl')
    faiss.write_index(index, index_path)
    with open(meta_path, 'w', encoding='utf-8') as f:
        for m in meta:
            f.write(json.dumps(m, ensure_ascii=False) + '\n')

def normalize(vecs):
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / np.clip(norms, 1e-8, None)

def row_to_text(row: pd.Series, file: str, sheet: str) -> str:
    items = [f"File={file}", f"Sheet={sheet}"]
    for col, val in row.items():
        if pd.isnull(val):
            continue
        if isinstance(val, (float, int)):
            sval = str(val)
        elif hasattr(val, 'isoformat'):
            sval = val.isoformat()
        else:
            sval = str(val).strip().replace('\n', ' ')
        sval = ' '.join(sval.split())
        items.append(f"{col}={sval}")
    return ', '.join(items)

def safe_table(df: pd.DataFrame, max_rows=10) -> str:
    if df.empty:
        return "(no data)"
    return df.head(max_rows).to_markdown(index=False)

def detect_ollama(host: str) -> bool:
    try:
        r = requests.get(f"{host}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def generate_with_ollama(prompt: str, model: str, host: str) -> str:
    try:
        import ollama
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception as e:
        return f"[Ollama error: {e}]"

def fallback_summarize(query: str, contexts: List[Dict[str, Any]]) -> str:
    q = query.lower()
    if any(word in q for word in ["count", "total", "how many"]):
        return f"Count: {len(contexts)} rows matched your query."
    else:
        snippets = '\n'.join([c['text'] for c in contexts])
        return f"Relevant records:\n{snippets}\n(End of retrieved snippets.)"


