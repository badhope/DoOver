from graph.state import AgentState
from time import time as get_current_time
from utils.logger import logger
from utils.ip_utils import get_country_by_ip
from typing import Any
import json
from langchain_core.messages import AIMessage

from llm.service import get_model
from tools.registry import search_tool
from graph.prompts import prompt_template
#初始化世界参数
async def init_world_params(state: AgentState) -> AgentState:
    time = get_current_time()
    country = await get_country_by_ip()
    logger.info("init_world_params:",{"world_info": {
        "time": time,
        "country": country,
    }})
    return {"world_info": {
        "time": time,
        "country": country,
    }}

# 获取用户输入
async def intake_node(state: AgentState) -> AgentState:
    raw_input = state.get("raw_input")
    if not raw_input:
        raise ValueError("raw_input is required")
    logger.info("intake_node:",{"raw_input": raw_input})
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
        logger.print(text, end="")

    final_text = "".join(chunks)
    return {"structured_scenario": final_text}
async def agent_node(state: AgentState):
    """
    【新增节点】：这是 ReAct 循环的大脑。
    负责调用 LLM，LLM 决定是回答还是调用工具。
    """
    model = get_model().bind_tools([search_tool])
    response = await model.ainvoke(state.get("messages",""))
    logger.info("agent_node:",{"messages": [response]})
    return {"messages": [response]}
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
