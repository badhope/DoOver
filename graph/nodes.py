from state import AgentState
from time import time as get_current_time
from loguru import logger
from utils.ip_utils import get_country_by_ip
from typing import Any
import json
#初始化世界参数
async def init_world_params(state: AgentState) -> AgentState:
    time = get_current_time()
    country = await get_country_by_ip()
    return {"world_info": {
        "time": time,
        "country": country,
    }}

# 获取用户输入
async def intake_node(state: AgentState) -> AgentState:
    raw_input = state.get("raw_input")
    if not raw_input:
        raise ValueError("raw_input is required")
    return {"raw_input": raw_input.strip()}

# 背景信息提取
def background_node(state: AgentState) -> dict[str, Any]:
    raw_input = state.get("raw_input", "")
    world_info = state.get("world_info", {})

    context = f"用户输入：{raw_input}\n用户ip信息：{world_info}"

    return {"structured_scenario": context}

