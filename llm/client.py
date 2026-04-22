from __future__ import annotations
from langchain_core.language_models import BaseChatModel
import json
import os
from pathlib import Path
from typing import Any

from llm.provider.openai_llm import create_openai_llm
from utils.load_config import load_json_config

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "provider.json"

def _get_active_provider_config(config: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    provider_name = config["active_llm_provider"]
    model_name = config["active_llm_model"]
    providers = config["llm_providers"]

    if provider_name not in providers:
        raise ValueError(f"Unknown llm provider instance: {provider_name}")

    provider_config = providers[provider_name]
    if model_name not in provider_config.get("models", []):
        raise ValueError(
            f"Model '{model_name}' is not configured under provider "
            f"instance '{provider_name}'"
        )

    return provider_name, model_name, provider_config


def create_provider_llm(
    model_name: str,
    provider_type: str,
    api_key: str,
    base_url: str,
    *,
    stream_usage: bool = True,
) -> BaseChatModel:
    normalized_model_name = str(model_name or "").strip()
    normalized_provider_type = str(provider_type or "").strip().lower()
    normalized_api_key = str(api_key or "").strip()
    normalized_base_url = str(base_url or "").strip()

    if not normalized_model_name:
        raise ValueError("model_name is required")
    if not normalized_api_key:
        raise ValueError("api_key is not set")
    if not normalized_base_url:
        raise ValueError("base_url is not set")

    if normalized_provider_type == "openai":
        return create_openai_llm(
            model_name=normalized_model_name,
            api_key=normalized_api_key,
            base_url=normalized_base_url,
            stream_usage=stream_usage,
        )

    raise ValueError(f"Unsupported llm provider type: {normalized_provider_type}")


def load_active_llm(config: dict[str, Any] | None = None) -> BaseChatModel:
    config = config or load_json_config(CONFIG_PATH)
    provider_name, model_name, provider_config = _get_active_provider_config(config)

    api_key = provider_config["api_key"]
    if not api_key:
        raise ValueError(f"api_key'{api_key}' is not set")

    base_url = provider_config["base_url"]
    provider_type = provider_config["type"]
    return create_provider_llm(
        model_name=model_name,
        provider_type=provider_type,
        api_key=api_key,
        base_url=base_url,
    )

def load_active_nostream_llm(config: dict[str, Any] | None = None) -> BaseChatModel:
    config = config or load_json_config(CONFIG_PATH)
    provider_name, model_name, provider_config = _get_active_provider_config(config)

    api_key = provider_config["api_key"]
    if not api_key:
        raise ValueError(f"api_key'{api_key}' is not set")

    base_url = provider_config["base_url"]
    provider_type = provider_config["type"]
    return create_provider_llm(
        model_name=model_name,
        provider_type=provider_type,
        api_key=api_key,
        base_url=base_url,
        stream_usage=False,
    )


__all__ = ["create_provider_llm", "load_active_llm", "load_active_nostream_llm"]
