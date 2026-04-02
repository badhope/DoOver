from time import time as get_current_time
from typing import Any, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from graph.prompts import prompt_template
from graph.state import AgentState
from llm.service import get_model
from tools.registry import active_tools
from utils.ip_utils import get_country_by_ip
from utils.logger import logger


async def init_world_params(state: AgentState) -> AgentState:
    time = get_current_time()
    country = await get_country_by_ip()
    logger.print("node:"+"init_world_params")
    return {
        "world_info": {
            "time": time,
            "country": country,
        }
    }


async def intake_node(state: AgentState) -> AgentState:
    raw_input = state.get("raw_input")
    if not raw_input:
        raise ValueError("raw_input is required")
    logger.print("node:"+"intake_node")
    return {
        "raw_input": raw_input.strip(),
        "messages": [HumanMessage(content=raw_input.strip())],
    }


async def background_node(state: AgentState) -> dict[str, Any]:
    raw_input = state.get("raw_input", "")
    world_info = state.get("world_info", {})
    prompt_messages = prompt_template.format_messages(
        raw_input=raw_input,
        world_info=world_info,
    )
    messages = state.get("messages", [])
    content = prompt_messages + messages
    model = get_model().bind_tools(active_tools)

    final_text = ""
    response: Any = None
    logger.print("node:"+"background_node")
    async for chunk in model.astream(content):
        chunk = cast(Any, chunk)
        text = chunk.content if isinstance(getattr(chunk, "content", None), str) else ""
        if text:
            logger.print("background_node_msg:"+text, end="")
            final_text += text
        if response is None:
            response = chunk
        else:
            response = response + chunk

    return {
        "structured_scenario": final_text,
        "messages": [cast(BaseMessage, response)],
    }


async def should_continue_bg(state: AgentState):
    background_refined = state.get("background_refined")
    if not background_refined:
        return "continue"
    return "end"


async def agent_node(state: AgentState):
    model = get_model().bind_tools(active_tools)
    messages = state.get("messages") or []
    response = await model.ainvoke(messages)
    logger.print("node:"+"agent_node")
    return {"messages": response}


def should_continue(state: AgentState):
    messages = state.get("messages", [])
    last_message = messages[-1]
    if not isinstance(last_message, AIMessage):
        return "end"

    if not last_message.tool_calls:
        return "end"
    return "continue"
