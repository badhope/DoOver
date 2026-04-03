import json

from langchain.tools import tool

from graph.pydantic_models import AlternativeActionList
from utils.websocket import emit_ws_event

#询问用户补充信息工具
@tool(name_or_callable="ask_user", return_direct=False)
async def ask_user(question: str, field: str = "follow_up") -> str:
    """
    Ask the user for missing information before continuing the analysis.
    """
    payload = {
        "question": question,
        "field": field,
    }
    emit_ws_event("ask_user", **payload)
    return json.dumps(payload, ensure_ascii=False)

#询问用户选择工具
async def ask_user_choice_impl(alternative_action_list: AlternativeActionList,field:str = "choose") -> str:
    """
    真正的业务逻辑：通知前端，让用户做选择
    """
    payload = {
        "alternative_action_list": alternative_action_list.model_dump(),
        "field": field,
    }
    emit_ws_event("ask_user_choice", **payload)
    return json.dumps(payload, ensure_ascii=False)
@tool(name_or_callable="ask_user_choice", return_direct=False)
async def ask_user_choice(alternative_action_list: AlternativeActionList) -> str:
    """
    Ask the user to choose from a list of options.
    """
    return await ask_user_choice_impl(alternative_action_list)
