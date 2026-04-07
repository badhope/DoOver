from pathlib import Path
from typing import Any

from utils.load_config import load_json_config, save_json_config
from utils.session import resolve_user_from_token

USER_CONF_PATH = Path("user/conf/user.json")
TOKEN_STORE_PATH = Path("user/data/tokens.json")


async def update_username_and_password(
    token: str | None,
    username: str,
    password: str,
) -> None:
    normalized_token = str(token or "").strip()
    normalized_username = str(username or "").strip()
    normalized_password = str(password or "").strip()

    if not normalized_token:
        raise ValueError("token is required")
    if not normalized_username:
        raise ValueError("username is required")
    if not normalized_password:
        raise ValueError("password is required")

    current_user = await resolve_user_from_token(normalized_token)
    if not current_user:
        raise PermissionError("invalid token")

    conf = load_json_config(USER_CONF_PATH)
    conf["user_name"] = normalized_username
    conf["user_key"] = normalized_password
    save_json_config(USER_CONF_PATH, conf)

    if not TOKEN_STORE_PATH.exists():
        return

    token_store = load_json_config(TOKEN_STORE_PATH)
    tokens = token_store.get("tokens")
    if not isinstance(tokens, list):
        return

    updated_tokens: list[Any] = []
    for item in tokens:
        if isinstance(item, dict):
            item_token = str(item.get("token") or "").strip()
            item_user = str(item.get("user_name") or "").strip()
            if item_token == normalized_token or item_user == current_user:
                item["user_name"] = normalized_username
            updated_tokens.append(item)
            continue
        updated_tokens.append(item)

    token_store["tokens"] = updated_tokens
    save_json_config(TOKEN_STORE_PATH, token_store)
