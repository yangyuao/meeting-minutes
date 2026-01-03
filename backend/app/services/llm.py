from __future__ import annotations

import json
import logging
from typing import Generator

import requests

from ..settings import Settings

logger = logging.getLogger(__name__)


def generate_ollama_stream(
    settings: Settings,
    final_prompt: str,
) -> Generator[str, None, None]:
    payload = {
        "model": settings.ollama_model,
        "prompt": final_prompt,
        "stream": True,
    }

    try:
        with requests.post(settings.ollama_api, json=payload, stream=True) as response:
            if response.status_code != 200:
                logger.error("无法连接到 Ollama 模型，状态码: %d", response.status_code)
                yield "[错误] 无法连接到 Ollama 模型。"
                return

            for chunk in response.iter_content(chunk_size=None):
                if not chunk:
                    continue
                try:
                    text = chunk.decode("utf-8").strip()
                    data = json.loads(text)
                    response_text = data.get("response", "")
                    if response_text:
                        yield response_text
                except json.JSONDecodeError:
                    continue
    except Exception as exc:
        logger.error("请求 Ollama 模型时出错: %s", exc)
        yield f"[错误] 请求 Ollama 模型时出错: {exc}"


def generate_vllm_stream(
    settings: Settings,
    system_prompt: str,
    user_prompt: str,
) -> Generator[str, None, None]:
    prompt = system_prompt if system_prompt else settings.prompt_template
    payload = {
        "model": settings.vllm_model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.00,
        "stream": True,
    }

    try:
        with requests.post(
            settings.vllm_api, json=payload, stream=True, timeout=10
        ) as response:
            if response.status_code != 200:
                logger.error("无法连接到 vLLM 模型，状态码: %d", response.status_code)
                logger.error("响应内容: %s", response.text)
                yield f"响应内容: {response.text}"
                return

            for chunk in response.iter_content(chunk_size=None):
                if not chunk:
                    continue
                try:
                    text = chunk.decode("utf-8").strip()
                    if text.startswith("data:"):
                        data_str = text[5:].strip()
                        if data_str == "[DONE]":
                            break
                        data = json.loads(data_str)
                        content = (
                            data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
    except Exception as exc:
        logger.error("请求 vLLM 模型时出错: %s", exc)
        yield f"[错误] 请求 vLLM 模型时出错: {exc}"


def unified_streamer(
    settings: Settings,
    system_prompt: str,
    user_prompt: str,
    is_production: bool,
) -> Generator[str, None, None]:
    if not is_production:
        yield from generate_ollama_stream(
            settings=settings,
            final_prompt=system_prompt + user_prompt,
        )
    else:
        yield from generate_vllm_stream(
            settings=settings,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
