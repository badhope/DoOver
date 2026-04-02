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
    agent_node
)
from graph.state import AgentState
from tools.registry import active_tools
from utils.logger import receive_websocket_event, start_websocket_server

graph = StateGraph(AgentState)

graph.add_node("init_world_params", init_world_params)
graph.add_node("intake_node", intake_node)
graph.add_node("background_node", background_node)
graph.add_node("tool_node", ToolNode(tools=active_tools))
graph.add_node("wait_user_node", wait_user_node)
graph.add_node("agent_node", agent_node)

graph.set_entry_point("init_world_params")

graph.add_edge("init_world_params", "intake_node")
graph.add_edge("intake_node", "background_node")
graph.add_edge("background_node", "agent_node")
graph.add_conditional_edges(
    "agent_node",
    should_continue,
    {
        "continue": "tool_node",
        "end": END,
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
