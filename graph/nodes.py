from state import AgentState
from time import time as get_current_time
from loguru import logger
from utils.ip_utils import get_country_by_ip
from typing import Any
import json
from langchain_core.messages import AIMessage

from llm.service import get_model
from graph.prompts import prompt_template
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
async def background_node(state: AgentState) -> dict[str, Any]:
    raw_input = state.get("raw_input", "")
    world_info = state.get("world_info", {})
    prompt = prompt_template.format(raw_input=raw_input, world_info=world_info)
    model = get_model()
    chunks = []
    async for chunk in model.astream(prompt):
        text = chunk.content if hasattr(chunk, "content") else str(chunk)
        chunks.append(text)

        # TODO: 推给前端
        # 这里不是 return
        # 而是通过 graph stream / callback / websocket 把 text 推给前端

    final_text = "".join(chunks)
    return {"structured_scenario": final_text}

# 判断是否继续
def should_continue(state: AgentState):
    messages = state.get("messages", [])
    if not messages:
        return "end"

    last_message = messages[-1]
    if not isinstance(last_message, AIMessage):
        return "end"

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
