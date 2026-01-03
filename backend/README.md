# Meeting Minutes Backend

This backend runs the refactored FastAPI app located under `backend/app/`. The entrypoint is `backend/main.py`.

## Prerequisites
- Python 3.10+ recommended
- A running MySQL instance (if you want DB persistence)
- Model assets configured via environment variables (ASR/VLLM/Ollama)

## Environment Variables
Configure via `.env` (loaded automatically) or your shell:

- `HOST` (default: `0.0.0.0`)
- `PORT` (default: `8002`)
- `DEBUG` (`true`/`false`)
- `CORS_ORIGINS` (comma-separated)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `OLLAMA_API`, `OLLAMA_MODEL`
- `VLLM_API`, `VLLM_MODEL`
- `PRODUCTION_IP`
- `ASR_MODEL`, `VAD_MODEL`, `PUNC_MODEL`, `SPK_MODEL`, `DEVICE`
- `HOTWORDS_PATH` (defaults to `backend/hotwords.txt`)
- `PPT_TEMPLATE` (defaults to `backend/会议纪要模板.docx`)
- `AUDIO_DIR` (defaults to `backend/audio_files`)

## Run (standard venv)
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn python-dotenv requests funasr torch pymysql python-docx
python backend/main.py
```

## Run (conda)
```bash
conda create -n meeting-minutes python=3.10 -y
conda activate meeting-minutes
pip install fastapi uvicorn python-dotenv requests funasr torch pymysql python-docx
python backend/main.py
```

## Run (uv)
```bash
uv venv
source .venv/bin/activate
uv pip install fastapi uvicorn python-dotenv requests funasr torch pymysql python-docx
python backend/main.py
```

## Notes
- The legacy `backend/test.py` is kept intact but is no longer the recommended entrypoint.
- `backend/app/main.py` exports the FastAPI `app` if you prefer to run with `uvicorn` directly:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8002
```
