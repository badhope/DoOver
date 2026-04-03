import json
from time import time as get_current_time
from typing import Any, cast

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage,SystemMessage
from langchain.agents.structured_output import ToolStrategy
from graph.prompts import prompt_template,refine_prompt,turn_prompt_template
from graph.state import AgentState
from graph.pydantic_models import AlternativeActionList
from llm.service import get_model,get_nostream_model
from tools.registry import active_tools
from tools.interaction import ask_user_choice_impl
from utils.ip_utils import get_country_by_ip
from utils.logger import logger
from utils.websocket import emit_ws_event, receive_websocket_event


# 初始化世界参数节点
async def init_world_params(state: AgentState) -> AgentState:
    logger.info("init_world_params")
    logger.print("node:" + "init_world_params")
    time = get_current_time()
    country = await get_country_by_ip()
    return {
        "world_info": {
            "time": time,
            "country": country,
        }
    }


# 初次获取用户输入输入节点
async def intake_node(state: AgentState) -> AgentState:
    logger.info("intake_node")
    logger.print("node:" + "intake_node")
    raw_input = state.get("raw_input")
    if not raw_input:
        raise ValueError("raw_input is required")
    return {
        "raw_input": raw_input.strip(),
        "messages": [HumanMessage(content=raw_input.strip())],
    }

# 分析获取背景信息节点
async def background_node(state: AgentState) -> dict[str, Any]:
    logger.info("background_node")
    logger.print("node:" + "background_node")
    raw_input = state.get("raw_input", "")
    world_info = state.get("world_info", {})
    prompt_messages = prompt_template.format_messages(
        raw_input=raw_input,
        world_info=world_info,
    )
    messages = state.get("messages", [])
    content = prompt_messages + messages
    model = get_model()

    final_text = ""
    response: Any = None

    async for chunk in model.astream(content):
        chunk = cast(Any, chunk)
        text = chunk.content if isinstance(getattr(chunk, "content", None), str) else ""
        if text:
            logger.print("background_node_msg:" + text, end="")
            final_text += text
        if response is None:
            response = chunk
        else:
            response = response + chunk

    return {
        "structured_scenario": final_text,
        "messages": [cast(BaseMessage, response)],
    }

# 等待用户补充信息节点
async def wait_user_node(state: AgentState) -> AgentState:
    logger.info("wait_user_node")
    logger.print("node:" + "wait_user_node")
    field = "follow_up"
    recent_tool_messages: list[ToolMessage] = []

    for message in reversed(state.get("messages", [])):
        if isinstance(message, ToolMessage):
            recent_tool_messages.append(message)
        else:
            break
    recent_tool_messages.reverse()

    for message in reversed(recent_tool_messages):
        if getattr(message, "name", None) != "ask_user":
            continue
        try:
            payload = json.loads(cast(str, message.content))
        except (TypeError, json.JSONDecodeError):
            payload = {}
        if isinstance(payload, dict):
            field = str(payload.get("field") or field)
        break

    event = await receive_websocket_event("user_answer")
    answer_field = str(event.get("field") or field)
    answer = str(event.get("answer") or "").strip()
    emit_ws_event("user_answer_received", field=answer_field, answer=answer)
    return {
        "messages": [HumanMessage(content=f"用户补充信息（{answer_field}）：{answer}")],
    }

# 分析调用工具节点
async def agent_node(state: AgentState):
    logger.info("agent_node")
    logger.print("node:" + "agent_node")
    model = get_model().bind_tools(active_tools)
    messages = state.get("messages") or []
    prompt = messages + [refine_prompt]
    response = await model.ainvoke(prompt)
    return {"messages": response}

# 判断是否继续
def should_continue(state: AgentState):
    logger.info("should_continue")
    logger.print("node:" + "should_continue")
    messages = state.get("messages", [])
    if not messages:
        logger.info("should_continue -> end (no messages)")
        return "end"

    last_message = messages[-1]
    if not isinstance(last_message, AIMessage):
        logger.info(f"should_continue -> end (last={type(last_message).__name__})")
        return "end"

    route = "continue" if last_message.tool_calls else "end"
    logger.info(f"should_continue -> {route}; tool_calls={last_message.tool_calls}")
    return route


# 判断是否等待用户
def should_wait_for_user(state: AgentState):
    logger.info("should_wait_for_user")
    logger.print("node:" + "should_wait_for_user")
    recent_tool_messages: list[ToolMessage] = []

    for message in reversed(state.get("messages", [])):
        if isinstance(message, ToolMessage):
            recent_tool_messages.append(message)
        else:
            break
    recent_tool_messages.reverse()

    for message in recent_tool_messages:
        if getattr(message, "name", None) == "ask_user":
            return "wait"
    return "continue"

#输出转机的节点
async def turn_node(state: AgentState) -> AgentState:
    logger.info("turn_node")
    logger.print("node:" + "turn_node")
    structured_scenario = state.get("structured_scenario")
    model = get_nostream_model().with_structured_output(AlternativeActionList)
    prompt = turn_prompt_template.format_messages(
        messages = structured_scenario,
        method="function_calling"
    )
    raw_response = await model.ainvoke(prompt)
    response = AlternativeActionList.model_validate(raw_response)
    return {
        "turning_event": response.items
    }

#用户选择节点
async def user_choice_node(state: AgentState) -> AgentState:
    logger.info("user_choice_node")
    logger.print("node:" + "user_choice_node")
    turning_event = state.get("turning_event")
    field = "choose"
    if turning_event is None:
        raise ValueError("turning_event 缺失")
    if not isinstance(turning_event, list):
        raise TypeError(f"turning_event 类型错误: {type(turning_event)}")
    await ask_user_choice_impl(
        AlternativeActionList(items=turning_event)
    )
    event = await receive_websocket_event("user_choice")
    answer_field = str(event.get("field") or field)
    answer = str(event.get("user_choice") or "").strip()
    logger.info(f"用户选择: {answer_field}: {answer}")
    emit_ws_event("user_answer_received", field=answer_field, answer=answer)
    return {
        "messages": [HumanMessage(content=f"用户选择信息（{answer_field}）：{answer}")],
    }# 角色节点
async def role_node(state: AgentState) -> AgentState:
    logger.info("role_node")

    return state
