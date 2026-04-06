import asyncio
from contextlib import suppress
from functools import partial

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
from utils.websocket import (
    create_session,
    list_sessions,
    receive_session_event,
    reset_current_session,
    set_current_session,
    start_websocket_server,
)

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

SESSION_DISCOVERY_INTERVAL_SECONDS = 0.5
_session_workers: dict[str, asyncio.Task[None]] = {}

from IPython.display import Image,display

display(Image(app.get_graph().draw_mermaid_png()))


async def run_session(session_id: str) -> None:
    """
    运行单个 session 对应的 graph worker。

    一个 session 对应一个常驻协程，它会一直做两件事：
    1. 等待这个 session 的 user_input 事件
    2. 收到输入后，启动一次新的 graph 执行

    这里要注意：
    - graph.compile() 得到的 app 是共享的
    - 但每次 app.astream(...) 传入的 state 都是当前这次输入新建的
    - session 隔离靠的是“事件队列 + 当前上下文里的 session_id”，不是靠多实例 app
    """
    # 把当前协程绑定到这个 session。
    # 这样 graph 内部的 logger.print / emit_ws_event / receive_websocket_event
    # 即使不显式传 session_id，也能自动命中当前会话。
    token = set_current_session(session_id)
    try:
        while True:
            # 每个 session 只消费属于自己的 user_input 事件。
            event = await receive_session_event("user_input", session_id=session_id)
            text = str(event.get("text") or "").strip()
            if not text:
                continue

            # 每次新的顶层用户输入，都会新建一份独立的运行时 state。
            # 所以不同用户/不同轮输入，不会共享同一个 AgentState 对象。
            state: AgentState = {"raw_input": text}
            async for _step in app.astream(state, stream_mode="values"):
                # 这里不消费 step 的具体内容，因为当前项目的实时输出主要通过
                # logger.print() / emit_ws_event() 直接走 session 总线推给前端。
                pass
    finally:
        # 无论 worker 是正常退出、报错还是被 cancel，都必须恢复上下文，
        # 否则后续复用同一事件循环时可能把 session 串到别的协程里。
        reset_current_session(token)


def _on_session_worker_done(session_id: str, task: asyncio.Task[None]) -> None:
    """
    session worker 的结束回调。

    作用有两个：
    1. 把已经结束的 task 从注册表里移除
    2. 主动触发 task.exception()，避免某些异常悄悄被吞掉
    """
    current = _session_workers.get(session_id)
    if current is task:
        _session_workers.pop(session_id, None)

    with suppress(asyncio.CancelledError):
        task.exception()


def ensure_session_worker(session_id: str) -> asyncio.Task[None]:
    """
    确保某个 session 有且只有一个存活中的 worker。

    这是一个幂等接口：
    - 如果该 session 的 worker 已经在跑，直接返回旧 task
    - 如果没有，就创建新的 worker
    """
    normalized = create_session(session_id)
    existing = _session_workers.get(normalized)
    if existing is not None and not existing.done():
        return existing

    worker = asyncio.create_task(
        run_session(normalized),
        name=f"doover-session-{normalized}",
    )
    worker.add_done_callback(partial(_on_session_worker_done, normalized))
    _session_workers[normalized] = worker
    return worker


async def stop_session_workers() -> None:
    """
    停止所有 session worker。

    停止顺序是：
    1. 先统一 cancel
    2. 再 await 它们结束

    这样做比边遍历边等待更稳，避免某个 worker 卡住导致其他 worker 迟迟收不到取消信号。
    """
    workers = [task for task in _session_workers.values() if not task.done()]
    for task in workers:
        task.cancel()

    for task in workers:
        with suppress(asyncio.CancelledError):
            await task

    _session_workers.clear()


async def run_doc():
    """
    运行整个后端入口。

    当前职责：
    1. 启动 websocket 服务
    2. 周期性扫描已创建的 session
    3. 为每个 session 确保对应的 worker 已启动

    这里现在还采用“扫描 session -> 懒启动 worker”的方式，
    是为了尽量少改现有结构。后续如果接 FastAPI，更推荐在创建 session 时
    直接显式调用 ensure_session_worker(session_id)。
    """
    await start_websocket_server("localhost", 8765)

    try:
        while True:
            for session_id in list_sessions():
                # 只要某个 session 已经被创建出来，就确保它背后的 graph worker 存在。
                ensure_session_worker(session_id)
            await asyncio.sleep(SESSION_DISCOVERY_INTERVAL_SECONDS)
    finally:
        await stop_session_workers()


if __name__ == "__main__":
    
    asyncio.run(run_doc())
