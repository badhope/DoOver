import asyncio

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from graph.nodes import background_node, init_world_params, intake_node, should_continue,agent_node
from graph.state import AgentState
from tools.registry import active_tools

graph = StateGraph(AgentState)

graph.add_node("init_world_params", init_world_params)
graph.add_node("intake_node", intake_node)
graph.add_node("background_node", background_node)
graph.add_node("should_continue", should_continue)
graph.add_node("tool_node", ToolNode(tools=active_tools))
graph.add_node("agent", agent_node)

graph.set_entry_point("init_world_params")

state: AgentState = {"raw_input": input("请输入你的经历: ")}

graph.add_edge("init_world_params", "intake_node")
graph.add_edge("intake_node", "background_node")
graph.add_edge("background_node", "agent")
graph.add_conditional_edges(
    "tool_node",
    should_continue,
    {
        "continue": "background_node",
        "end": END,
    },
)
graph.add_edge("tool_node", "agent") 
app = graph.compile()

async def run_doc():

    async for step in app.astream(state,stream_mode="values"):
        if "messages" in step:
            print(step["messages"])

if __name__ == "__main__":
    asyncio.run(run_doc())
