from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import torch
from funasr import AutoModel

logger = logging.getLogger(__name__)


@dataclass
class ASRConfig:
    asr_model: str
    vad_model: str
    punc_model: str
    spk_model: str
    device: str


class ModelManager:
    def __init__(self, config: ASRConfig):
        self._config = config
        self._model = None

    def get(self):
        if self._model is None:
            logger.info("正在加载语音识别模型...")
            self._model = AutoModel(
                model=self._config.asr_model,
                vad_model=self._config.vad_model,
                punc_model=self._config.punc_model,
                spk_model=self._config.spk_model,
                disable_update=True,
                device=self._config.device,
            )
            logger.info("语音识别模型加载完成")
        else:
            logger.info("使用已缓存的模型实例")
        return self._model


def clean_speech(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    noise_words = ["嗯", "啊", "哦", "呃", "哈", "这个", "那个", "然后", "就是", "的话"]
    for word in noise_words:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def process_transcript(input_file: Path, output_file: Path) -> None:
    logger.debug("开始处理转录文件: %s", input_file)
    with input_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if data and data[0].get("timestamp"):
        data[0].pop("timestamp")

    processed = []
    current_spk = None
    current_batch: list[dict[str, Any]] = []

    for item in data[0].get("sentence_info", []):
        try:
            if not isinstance(item, dict):
                continue

            spk = item.get("spk")
            text = str(item.get("text", ""))
            start = float(item.get("start", 0))
            end = float(item.get("end", 0))

            if spk == current_spk:
                current_batch.append({"text": text, "start": start, "end": end})
            else:
                if current_batch:
                    processed.append(
                        {
                            "text": " ".join([s["text"] for s in current_batch]),
                            "spk": current_spk,
                            "start": min(s["start"] for s in current_batch),
                            "end": max(s["end"] for s in current_batch),
                        }
                    )
                current_batch = [{"text": text, "start": start, "end": end}]
                current_spk = spk
        except Exception as exc:
            logger.error("处理转录数据时发生异常: %s", exc)
            continue

    if current_batch and current_batch[0].get("text"):
        processed.append(
            {
                "text": " ".join([s["text"] for s in current_batch]),
                "spk": current_spk,
                "start": min(s["start"] for s in current_batch),
                "end": max(s["end"] for s in current_batch),
            }
        )

    data[0]["sentence_info"] = processed

    with output_file.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    logger.debug("转录处理完成，输出文件: %s", output_file)


def ms_to_timestamp(milliseconds: float) -> str:
    seconds = milliseconds / 1000
    td = timedelta(seconds=seconds)
    return str(td).split(".")[0]


def process_json(input_file: Path, output_file: Path) -> None:
    logger.debug("开始处理JSON文件: %s", input_file)
    with input_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    with output_file.open("w", encoding="utf-8") as handle:
        for item in data:
            for sentence in item.get("sentence_info", []):
                speaker = f"发言人{sentence['spk']}"
                text = "".join(sentence.get("text", "").split(" "))
                handle.write(f"{speaker}: {text}\n")
    logger.debug("JSON处理完成，输出文件: %s", output_file)


def run_asr(
    model_manager: ModelManager,
    audio_path: Path,
    hotwords_path: Path,
    output_dir: Path,
) -> tuple[str, Path, Path]:
    model = model_manager.get()
    logger.info("开始语音识别...")
    res = model.generate(
        input=str(audio_path),
        batch_size_s=64,
        hotword=str(hotwords_path),
    )
    torch.set_num_threads(4)

    temp_json = output_dir / "temp.json"
    processed_json = output_dir / "processed.json"
    output_txt = output_dir / "output.txt"

    with temp_json.open("w", encoding="utf-8") as handle:
        json.dump(res, handle, ensure_ascii=False, indent=2)

    process_transcript(temp_json, processed_json)
    process_json(processed_json, output_txt)

    with output_txt.open("r", encoding="utf-8") as handle:
        full_text = handle.read()

    logger.info("语音识别完成")
    logger.debug("语音识别结果: %s", full_text)

    temp_json.unlink(missing_ok=True)
    processed_json.unlink(missing_ok=True)

    return full_text, audio_path, output_txt
