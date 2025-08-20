import os

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
INDEX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'index'))
HF_CACHE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models', 'hf'))

# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Hugging Face cache
os.environ["HF_HOME"] = HF_CACHE
os.environ["TRANSFORMERS_CACHE"] = HF_CACHE

# FAISS
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, 'faiss.index')
FAISS_META_PATH = os.path.join(INDEX_DIR, 'meta.jsonl')
FAISS_TOP_K = int(os.getenv("TOP_K", 5))

# Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:instruct")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Gradio
GRADIO_PORT = int(os.getenv("GRADIO_PORT", 7860))
GRADIO_SHARE = False

# Safety
MAX_ROWS_PREVIEW = 20
MAX_TOKENS_PER_CHUNK = 512
