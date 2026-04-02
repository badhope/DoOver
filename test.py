import asyncio
from typing import Any
from utils.logger import logger, start_websocket_server, receive_websocket_message
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from graph.nodes import background_node, init_world_params, intake_node, should_continue, agent_node, should_continue_bg
from graph.state import AgentState
from tools.registry import active_tools, search_tool

graph = StateGraph(AgentState)

graph.add_node("init_world_params", init_world_params)
graph.add_node("intake_node", intake_node)
graph.add_node("background_node", background_node)
graph.add_node("tool_node", ToolNode(tools=[search_tool]))
graph.add_node("agent", agent_node)

graph.set_entry_point("init_world_params")


graph.add_edge("init_world_params", "intake_node")
graph.add_edge("intake_node", "background_node")
graph.add_conditional_edges(
    "background_node",
    should_continue,
    {
        "continue": "tool_node",
        "end": END,
    },
)
graph.add_edge("tool_node", "background_node")
app = graph.compile()

#from IPython.display import Image,display

#display(Image(app.get_graph().draw_mermaid_png()))


async def run_doc():
    await start_websocket_server("localhost", 8765)
    state: AgentState = {"raw_input": await receive_websocket_message()}
    async for step in app.astream(state, stream_mode="values"):
        pass


if __name__ == "__main__":
    asyncio.run(run_doc())
