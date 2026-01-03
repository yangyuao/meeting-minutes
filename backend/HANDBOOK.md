# Backend Run Handbook (Step-by-Step)

This handbook walks through running the legacy backend in `backend/test.py` using the `meeting-minutes` conda environment.

## 1) Verify conda is available
```bash
conda --version
```

## 2) Create or update the conda environment
If the environment does not exist yet:
```bash
conda create -n meeting-minutes python=3.10 -y
```

Activate it:
```bash
conda activate meeting-minutes
```

## 3) Install Python dependencies
From the repo root:
```bash
pip install -r backend/requirements.txt
```

Note: The legacy `test.py` requires `torchaudio` (via `funasr`). If you see a `ModuleNotFoundError: torchaudio`, install it explicitly:
```bash
pip install torchaudio
```

If you need a CUDA build, use the PyTorch selector to match your CUDA version.

## 4) Prepare environment variables
Create a `.env` file at the repo root (or export variables in your shell). Minimal example:
```bash
HOST=0.0.0.0
PORT=8002
DEBUG=false
CORS_ORIGINS=http://localhost:5173
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=meeting_minutes
```

Optional model/service settings (modelcard IDs recommended):
```bash
OLLAMA_API=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen3:4b
VLLM_API=http://10.8.2.21:8999/v1/chat/completions
VLLM_MODEL=/home/ubuntu/models/Qwen3-8B
PRODUCTION_IP=10.6.2.178
ASR_MODEL=iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
VAD_MODEL=iic/speech_fsmn_vad_zh-cn-16k-common-pytorch
PUNC_MODEL=iic/punc_ct-transformer_cn-en-common-vocab471067-large
SPK_MODEL=iic/speech_campplus_sv_zh-cn_16k-common
DEVICE=cuda:0
MODELSCOPE_CACHE=/home/teddy/.cache/modelscope
```

## 5) Run the backend (legacy `test.py`)
From the repo root:
```bash
conda run -n meeting-minutes python backend/test.py
```

## 6) Verify the service is running
Open a new shell and run:
```bash
curl http://localhost:8002/
```
Expected response:
```json
{"message":"Backend is running"}
```

## 7) Common issues
- `ModuleNotFoundError: torchaudio`
  - Install `torchaudio` in the same conda environment:
    ```bash
    pip install torchaudio
    ```
- ASR models not found
  - Ensure the `ASR_MODEL`, `VAD_MODEL`, `PUNC_MODEL`, `SPK_MODEL` paths exist.
- DB errors
  - Check `DB_HOST`, `DB_PORT`, credentials, and that MySQL is reachable.

## 8) Stop the server
Use `Ctrl+C` in the terminal running the server.
