from __future__ import annotations
from langchain_core.language_models import BaseChatModel
import json
import os
from pathlib import Path
from typing import Any

from llm.provider.kimi_llm import create_moonshot_llm
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


def load_active_llm(config: dict[str, Any] | None = None) -> BaseChatModel:
    config = config or load_json_config(CONFIG_PATH)
    provider_name, model_name, provider_config = _get_active_provider_config(config)

    api_key = provider_config["api_key"]
    if not api_key:
        raise ValueError(f"api_key'{api_key}' is not set")

    base_url = provider_config["base_url"]
    provider_type = provider_config["type"]

    if provider_type == "moonshot":
        return create_moonshot_llm(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    if provider_type == "openai":
        return create_openai_llm(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )

    raise ValueError(f"Unsupported llm provider type: {provider_type}")


__all__ = ["load_active_llm"]
