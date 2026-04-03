import json

from langchain.tools import tool

from utils.websocket import emit_ws_event


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
