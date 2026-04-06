import asyncio

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from graph.nodes import (
    background_node,
    init_world_params,
    intake_node,
    should_continue,
    should_wait_for_user,
    wait_user_node,
    agent_node,
    turn_node,
    user_choice_node,
    create_role_node,
    continue_to_roles,
    role_node,
    analyze_interaction_node,
    wait_for_interaction_node,
    should_wait_for_role_interaction,
    continue_next_node
)
from graph.state import AgentState
from tools.registry import active_tools,interact_with_role
from utils.websocket import receive_websocket_event, start_websocket_server

graph = StateGraph(AgentState)

graph.add_node("init_world_params", init_world_params)
graph.add_node("intake_node", intake_node)
graph.add_node("background_node", background_node)
graph.add_node("tool_node", ToolNode(tools=active_tools))
graph.add_node("wait_user_node", wait_user_node)
graph.add_node("agent_node", agent_node)
graph.add_node("turn_node",turn_node)
graph.add_node("user_choice_node", user_choice_node)
graph.add_node("role_node", role_node)
graph.add_node("create_role_node", create_role_node)
graph.add_node("analyze_interaction_node",analyze_interaction_node)
graph.add_node("tool_node2", ToolNode(tools=[interact_with_role]))
graph.add_node("wait_for_interaction_from_analyze", wait_for_interaction_node)
graph.add_node("continue_next_node", continue_next_node)
graph.set_entry_point("init_world_params")

graph.add_edge("init_world_params", "intake_node")
graph.add_edge("intake_node", "background_node")
graph.add_edge("background_node", "agent_node")
graph.add_node("tool_node3", ToolNode(tools=[interact_with_role]))
graph.add_node("wait_for_interaction_from_continue", wait_for_interaction_node)
graph.add_conditional_edges(
    "agent_node",
    should_continue,
    {
        "continue": "tool_node",
        "end": "turn_node",
    },
)
graph.add_conditional_edges(
    "tool_node",
    should_wait_for_user,
    {
        "wait": "wait_user_node",
        "continue": "background_node",
    },
)
graph.add_edge("wait_user_node", "background_node")
graph.add_edge("turn_node", "user_choice_node")
graph.add_edge("user_choice_node", "create_role_node")
graph.add_conditional_edges("create_role_node", continue_to_roles, ["role_node"])
graph.add_edge("role_node", "analyze_interaction_node")
graph.add_conditional_edges(
    "analyze_interaction_node",
    should_continue,
    {
        "continue": "tool_node2",
        "end": "continue_next_node",
    },
)
graph.add_conditional_edges(
    "tool_node2",
    should_wait_for_role_interaction,
    {
        "wait": "wait_for_interaction_from_analyze",
        "continue": "analyze_interaction_node",
    },
)
graph.add_edge("wait_for_interaction_from_analyze", "analyze_interaction_node")
graph.add_conditional_edges(
    "continue_next_node",
    should_continue,
    {
        "continue": "tool_node3",
        "end": END,
    },
)
graph.add_conditional_edges(
    "tool_node3",
    should_wait_for_role_interaction,
    {
        "wait": "wait_for_interaction_from_continue",
        "continue": "continue_next_node",
    },
)
graph.add_edge("wait_for_interaction_from_continue", "continue_next_node")
app = graph.compile()

from IPython.display import Image,display

display(Image(app.get_graph().draw_mermaid_png()))
async def run_doc():


    await start_websocket_server("localhost", 8765)
    while True:
        event = await receive_websocket_event("user_input")
        text = str(event.get("text") or "").strip()
        if not text:
            continue
        state: AgentState = {"raw_input": text}
        async for _step in app.astream(state, stream_mode="values"):
            pass


if __name__ == "__main__":
    
    asyncio.run(run_doc())
