import os
import gradio as gr
import numpy as np
from sentence_transformers import SentenceTransformer
from config import *
from utils import load_faiss, normalize, detect_ollama, generate_with_ollama, fallback_summarize
import faiss
import json
import subprocess
import threading

os.environ["HF_HOME"] = HF_CACHE
os.environ["TRANSFORMERS_CACHE"] = HF_CACHE

index, meta = load_faiss(INDEX_DIR)
model = None
ollama_ok = detect_ollama(OLLAMA_HOST)

model_lock = threading.Lock()
def get_model():
    global model
    with model_lock:
        if model is None:
            model = SentenceTransformer(EMBEDDING_MODEL)
        return model

def retrieve(query, top_k=FAISS_TOP_K):
    embed = get_model().encode([query])
    embed = normalize(embed)
    D, I = index.search(embed.astype(np.float32), top_k)
    hits = []
    for idx in I[0]:
        if idx < 0 or idx >= len(meta):
            continue
        hits.append(meta[idx])
    return hits

def build_prompt(query, contexts):
    context_str = "\n".join([f"{i+1}) {c['text']}" for i, c in enumerate(contexts)])
    prompt = f"System: You are an internal analytics assistant. Answer ONLY from the provided context.\nIf the answer isn’t in context, say you don’t have enough data.\nCite the records you used (file/sheet/row).\nContext:\n{context_str}\nUser question: {query}"
    return prompt

def answer_fn(message, history):
    contexts = retrieve(message)
    if ollama_ok:
        prompt = build_prompt(message, contexts)
        answer = generate_with_ollama(prompt, OLLAMA_MODEL, OLLAMA_HOST)
    else:
        answer = fallback_summarize(message, contexts)
    citations = "\n".join([f"{c['file']} / {c['sheet']} / row {c['row_idx']}" for c in contexts])
    return answer, citations

def rebuild_index():
    proc = subprocess.run(["python", "ingest.py"], capture_output=True, text=True)
    global index, meta
    index, meta = load_faiss(INDEX_DIR)
    return f"Index rebuilt. Output:\n{proc.stdout}\n{proc.stderr}"

with gr.Blocks() as demo:
    gr.Markdown("# Local Analytics Chatbot (Excel QA)")
    with gr.Row():
        with gr.Column():
            user_input = gr.Textbox(label="Your Question", placeholder="Ask a question about your Excel data...")
            submit_btn = gr.Button("Send")
            clear_btn = gr.Button("Clear")
            rebuild_btn = gr.Button("Rebuild Index")
        with gr.Column():
            answer_box = gr.Textbox(label="Answer", interactive=False)
            citations_box = gr.Textbox(label="Citations (file/sheet/row)", interactive=False)

    def on_submit(question):
        return answer_fn(question, None)

    submit_btn.click(on_submit, inputs=user_input, outputs=[answer_box, citations_box])
    clear_btn.click(lambda: ("", ""), None, [answer_box, citations_box])
    rebuild_btn.click(lambda: rebuild_index(), None, None)

demo.launch(server_port=GRADIO_PORT, share=GRADIO_SHARE)
