import asyncio
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.load_config import load_json_config, save_json_config

AUTH_COOKIE_KEY = "doover_token"
USER_CONF_PATH = Path("user/conf/user.json")
TOKEN_STORE_PATH = Path("user/data/tokens.json")

_token_store_lock = asyncio.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_user_conf() -> dict[str, str]:
    conf = load_json_config(USER_CONF_PATH)
    return {
        "user_name": str(conf.get("user_name") or "").strip(),
        "user_key": str(conf.get("user_key") or "").strip(),
    }


def _load_token_store() -> dict[str, list[dict[str, str]]]:
    if not TOKEN_STORE_PATH.exists():
        return {"tokens": []}

    data = load_json_config(TOKEN_STORE_PATH)
    raw_tokens = data.get("tokens")
    if not isinstance(raw_tokens, list):
        return {"tokens": []}

    normalized: list[dict[str, str]] = []
    for item in raw_tokens:
        if isinstance(item, dict):
            token = str(item.get("token") or "").strip()
            user_name = str(item.get("user_name") or "").strip()
            created_at = str(item.get("created_at") or "").strip()
            if token:
                normalized.append(
                    {
                        "token": token,
                        "user_name": user_name,
                        "created_at": created_at,
                    }
                )
        elif isinstance(item, str):
            token = item.strip()
            if token:
                normalized.append(
                    {"token": token, "user_name": "", "created_at": ""}
                )
    return {"tokens": normalized}


def _save_token_store(data: dict[str, Any]) -> None:
    tokens = data.get("tokens")
    if not isinstance(tokens, list):
        payload = {"tokens": []}
    else:
        payload = {"tokens": tokens}
    save_json_config(TOKEN_STORE_PATH, payload)


async def create_login_token(user_name: str) -> str:
    token = secrets.token_urlsafe(32)
    async with _token_store_lock:
        store = _load_token_store()
        store["tokens"] = [
            item
            for item in store["tokens"]
            if str(item.get("user_name") or "").strip() != user_name
        ]
        store["tokens"].append(
            {
                "token": token,
                "user_name": user_name,
                "created_at": _utc_now_iso(),
            }
        )
        _save_token_store(store)
    return token


async def resolve_user_from_token(token: str | None) -> str | None:
    normalized = str(token or "").strip()
    if not normalized:
        return None

    async with _token_store_lock:
        store = _load_token_store()
        for item in store["tokens"]:
            if str(item.get("token") or "").strip() == normalized:
                user_name = str(item.get("user_name") or "").strip()
                return user_name or None
    return None


async def revoke_token(token: str | None) -> None:
    normalized = str(token or "").strip()
    if not normalized:
        return

    async with _token_store_lock:
        store = _load_token_store()
        next_tokens = [
            item
            for item in store["tokens"]
            if str(item.get("token") or "").strip() != normalized
        ]
        if len(next_tokens) != len(store["tokens"]):
            _save_token_store({"tokens": next_tokens})

