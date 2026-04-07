"""用户会话管理模块，处理用户认证、令牌创建和验证等功能"""

import asyncio
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.load_config import load_json_config, save_json_config

# 认证Cookie键名
AUTH_COOKIE_KEY = "doover_token"
# 用户配置文件路径
USER_CONF_PATH = Path("user/conf/user.json")
# 令牌存储文件路径
TOKEN_STORE_PATH = Path("user/data/tokens.json")

# 令牌存储锁，用于异步安全访问
_token_store_lock = asyncio.Lock()


def _utc_now_iso() -> str:
    """获取当前UTC时间的ISO格式字符串"""
    return datetime.now(timezone.utc).isoformat()


def load_user_conf() -> dict[str, str]:
    """
    加载用户配置信息
    
    Returns:
        包含用户名和用户密钥的字典
    """
    conf = load_json_config(USER_CONF_PATH)
    return {
        "user_name": str(conf.get("user_name") or "").strip(),
        "user_key": str(conf.get("user_key") or "").strip(),
    }


def _load_token_store() -> dict[str, list[dict[str, str]]]:
    """
    从文件加载令牌存储数据
    
    Returns:
        包含令牌列表的字典
    """
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
    """
    将令牌数据保存到文件
    
    Args:
        data: 要保存的令牌数据
    """
    tokens = data.get("tokens")
    if not isinstance(tokens, list):
        payload = {"tokens": []}
    else:
        payload = {"tokens": tokens}
    save_json_config(TOKEN_STORE_PATH, payload)


async def create_login_token(user_name: str) -> str:
    """
    为指定用户创建登录令牌
    
    Args:
        user_name: 用户名
        
    Returns:
        生成的登录令牌
    """
    token = secrets.token_urlsafe(32)
    async with _token_store_lock:
        store = _load_token_store()
        # 移除该用户之前的令牌
        store["tokens"] = [
            item
            for item in store["tokens"]
            if str(item.get("user_name") or "").strip() != user_name
        ]
        # 添加新令牌
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
    """
    根据令牌解析用户
    
    Args:
        token: 登录令牌
        
    Returns:
        如果令牌有效则返回用户名，否则返回None
    """
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
    """
    撤销指定令牌
    
    Args:
        token: 要撤销的令牌
    """
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