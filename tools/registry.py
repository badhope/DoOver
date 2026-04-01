from loguru import logger
from pathlib import Path
from langchain.tools import tool 
import json
from utils.load_config import load_json_config
from tools.search import search_from_baidu

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "tools.json"
config = load_json_config(CONFIG_PATH)

active_tools = []
# 搜索引擎注册
active_providers = config.get("search", {}).get("active_search_provider", {})

tools_map = {
        "baidu": search_from_baidu
    }

search_tool = tools_map[active_providers]

active_tools.append(tools_map[active_providers])


__all__ = [
    "search_tool",
    "active_tools"
]