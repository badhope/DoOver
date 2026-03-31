from typing import TypedDict, Any
from langchain_core.messages import BaseMessage

# 定义 State (共享背包)
class AgentState(TypedDict,total=False):
    world_info:dict[str, Any]
    raw_input:str #用户原始输入
    structured_scenario:dict[str, Any] # 提取出的信息
    turning_event:str #关键转折点是什么
    chosen_action:str #用户做出的不同选择
    predicted_outcome:str | dict[str, Any] #模型预测的事件走向
    truth_check:str | dict[str, Any] #事件合理性检查
    final_answer:str #最终结果
    messages: list[BaseMessage]