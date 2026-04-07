from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from graph.pydantic_models import AlternativeActionNode,CharacterAgentNode
import operator

class AgentState(TypedDict, total=False):
    world_info: dict[str, Any]#世界信息
    raw_input: str#用户输入
    structured_scenario: str#结合显示总结的用户信息
    turning_event: list[AlternativeActionNode]#转折事件
    chosen_action: str#用户再次做出的选择
    predicted_outcome: str | dict[str, Any]#预测这次选择下可能的结果
    truth_check: str | dict[str, Any]#真实性检查
    final_answer: str#最终的答案
    messages: Annotated[list[BaseMessage], add_messages]#聊天消息
    roles_info:list[CharacterAgentNode]#生成的角色信息
    role_outputs: Annotated[list[str], operator.add]# 生成的角色输出的消息
