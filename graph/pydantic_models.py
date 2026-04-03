from pydantic import BaseModel, Field
from typing import List, Optional
# 关键节点替代做法
class AlternativeActionNode(BaseModel):
    """存在其他可行做法的关键节点"""
    key_moment: str = Field(description="存在选择空间的关键时刻")
    original_action: str = Field(description="当时实际采取的做法")
    alternative_action: str = Field(description="当时可以采取的其他做法")

# 关键节点替代做法列表
class AlternativeActionList(BaseModel):
    """关键节点替代做法列表"""
    items: List[AlternativeActionNode] = Field(
        default_factory=list,
        description="关键节点及其替代做法列表，最多 3 个"
    )


class CharacterAgentPrompt(BaseModel):
    """从用户经历中抽象出的角色信息"""
    name: str = Field(description="角色名字或称呼，不知道就用关系称呼")
    social_role: str = Field(description="角色身份，如母亲、前任、同事、领导")
    relation_to_user: str = Field(description="该角色与用户的关系")
    
    summary: str = Field(description="该角色的简要概括")
    
    observed_actions: List[str] = Field(
        default_factory=list,
        description="经历中明确出现过的行为"
    )
    observed_attitudes: List[str] = Field(
        default_factory=list,
        description="对用户表现出的态度"
    )
    shared_events: List[str] = Field(
        default_factory=list,
        description="与用户共同经历的关键事件"
    )
    
    communication_style: Optional[str] = Field(
        default=None,
        description="该角色的说话方式"
    )
    inferred_traits: List[str] = Field(
        default_factory=list,
        description="可谨慎推断的人格特征或动机"
    )
    
    knowledge_scope: List[str] = Field(
        default_factory=list,
        description="该角色知道的信息边界"
    )
    unknowns: List[str] = Field(
        default_factory=list,
        description="经历中缺失、不可确定的信息"
    )
    roleplay_rules: List[str] = Field(
        default_factory=list,
        description="扮演限制与规则"
    )

class RoleplayPrompt(BaseModel):
    """从用户经历中抽象出的角色扮演信息"""
    roles: List[CharacterAgentPrompt] = Field(default_factory=list,description="从用户经历中抽象出的角色扮演信息")