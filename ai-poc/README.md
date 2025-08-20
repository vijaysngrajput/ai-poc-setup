# Local Analytics Chatbot POC (Excel QA)

A fully local, offline ChatGPT-style chatbot that answers questions from three Excel files using a local LLM (Ollama), FAISS for vector search, and Gradio for chat UI. No paid APIs, no global installs, all caches local.

---

## Q0. How are dependencies managed so nothing breaks?
- Uses a dedicated Python 3.11 venv (`report_poc_sample`) with pinned versions in `requirements.txt`.
- Nothing is installed globally.
- Hugging Face caches are stored in `./models/hf` to avoid polluting your home directory.

## Q1. How does it get the base model?
- Uses Ollama with `llama3:instruct` as the local LLM.
- **Install Ollama:**
  - Download from https://ollama.com/download
  - Start the server:
    ```bash
    ollama serve &
    ollama pull llama3:instruct
    ```
- The app auto-detects Ollama. If not found, it falls back to a rule-based summary.

## Q2. How is data vectorized?
- Each Excel row is converted to a readable text string and embedded using `sentence-transformers/all-MiniLM-L6-v2`.
- Embeddings are L2-normalized and stored in FAISS.

## Q3. What vector database is used?
- FAISS (CPU) stored locally under `./index/` (`faiss.index` + `meta.jsonl`).
- To rebuild the index:
  ```bash
   source report_poc_sample/bin/activate   # or .\report_poc_sample\Scripts\Activate.ps1
  python ingest.py
  ```

## Q4. How is it integrated with Gradio?
- Uses Gradio ChatInterface in `app.py`.
- Keeps session history, streams LLM answers (when Ollama is available), and shows citations for each answer.

---

## Runbook

1. **Create venv and install dependencies**
    - On **Mac/Linux** (use a bash terminal):
       ```bash
       bash setup_env.sh
       ```
    - On **Windows** (use PowerShell):
       ```powershell
       .\setup_env.ps1
       ```
2. **(Optional but recommended) run Ollama locally and pull the model**
   ```bash
   ollama serve &
   ollama pull llama3:instruct
   ```
3. **Put the 3 Excel files into `./data/`**
   - 20230118-20240418-MovedLoads.xlsx
   - BI-Regions.xlsx
   - UserEmails.xlsx
4. **Build the FAISS index**
    - On **Mac/Linux** (bash):
       ```bash
       source report_poc_sample/bin/activate
       python ingest.py
       ```
    - On **Windows** (PowerShell):
       ```powershell
       .\report_poc_sample\Scripts\Activate.ps1
       python ingest.py
       ```
5. **Launch the chatbot**
   ```bash
   python app.py
   # Open http://localhost:7860
   ```

---

## Notes
- No external paid APIs.
- If Ollama is not running, the app still works in fallback mode.
- You can change models, top_k, ports in `config.py`.

---

## Acceptance Criteria
- After setup and running, you can ask:
  - "How many loads moved in March 2024?"
  - "List regions we operate in."
  - "Show email for John Doe."
- The bot retrieves relevant rows, answers, and shows which rows it used (citations).
- Nothing installs outside the repo; caches stay in `./models/hf`.

---

## Project Layout

```
ai-poc/
├─ README.md
├─ setup_env.sh
├─ setup_env.ps1
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ data/
│  ├─ 20230118-20240418-MovedLoads.xlsx
│  ├─ BI-Regions.xlsx
│  └─ UserEmails.xlsx
├─ models/
│  └─ hf/
├─ index/
│  ├─ faiss.index
│  └─ meta.jsonl
├─ app.py
├─ ingest.py
├─ config.py
└─ utils.py
```
