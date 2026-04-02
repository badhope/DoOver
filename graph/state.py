from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    world_info: dict[str, Any]
    raw_input: str
    structured_scenario: dict[str, Any] | str
    turning_event: str
    chosen_action: str
    predicted_outcome: str | dict[str, Any]
    truth_check: str | dict[str, Any]
    final_answer: str
    messages: Annotated[list[BaseMessage], add_messages]
    background_refined: bool
