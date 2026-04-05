from pathlib import Path

from tools.interaction import ask_user,ask_user_choice,interact_with_role
from tools.search import search_from_baidu, search_from_tavily
from utils.load_config import load_json_config

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "tools.json"
config = load_json_config(CONFIG_PATH)

active_tools = []
active_providers = config.get("search", {}).get("active_search_provider", {})

tools_map = {
    "baidu": search_from_baidu,
    "tavily": search_from_tavily,
}

search_tool = tools_map[active_providers]

#注册工具
active_tools.append(search_tool)
active_tools.append(ask_user)
active_tools.append(ask_user_choice)


__all__ = [
    "active_tools",
    "interact_with_role"
]
