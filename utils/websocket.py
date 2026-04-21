"""
1. 维护按 session 隔离的消息总线
2. 提供入站事件队列，供 graph 节点等待用户输入
3. 提供出站订阅队列，供 websocket / StreamingResponse 等传输层消费
4. 保留旧函数名，尽量兼容当前项目里还没改完的调用方

- SessionState 是“每个会话自己的消息空间”
- websocket_handler 只是把 websocket 连接挂到这个消息空间上
- graph 节点和 logger 并不直接关心 websocket，只关心“往当前 session 发消息”

后续如果切到 FastAPI StreamingResponse，这个文件的大部分逻辑仍然可以复用，
只需要把 websocket_handler 对应的 transport 换掉即可。
"""

import asyncio
import json
from collections import defaultdict
from contextlib import suppress
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, AsyncIterator
from urllib.parse import parse_qs, urlsplit

# 这里用 ContextVar 保存“当前协程上下文正在处理哪个 session”。
# 好处是：graph 节点、logger、工具函数不需要层层显式传 session_id，
# 只要它们运行在 run_session(session_id) 建立的上下文里，就能自动拿到当前会话。
_current_session_id: ContextVar[str | None] = ContextVar(
    "current_ws_session_id",
    default=None,
)
# 当前进程中的 websocket 服务实例。
_ws_server = None


@dataclass
class SessionState:
    """
    每个 session 独享的一组运行时状态。

    subscribers:
        所有订阅这个 session 输出流的消费者。
        目前 websocket 会为每个连接注册一个 asyncio.Queue[str]。

    raw_messages:
        保存这个 session 收到的原始入站消息。
        如果后面需要做审计、调试或通用消费，可以直接从这里读取。

    event_queues:
        按事件类型拆分后的队列，例如 user_input / user_answer / user_choice。
        graph 节点通常不会消费 raw_messages，而是直接按事件类型阻塞等待。
    """
    subscribers: set[asyncio.Queue[str]] = field(default_factory=set)
    raw_messages: asyncio.Queue[Any] = field(default_factory=asyncio.Queue)
    event_queues: dict[str, asyncio.Queue[dict[str, Any]]] = field(
        default_factory=lambda: defaultdict(asyncio.Queue)
    )
    meta: dict[str, Any] = field(default_factory=dict)


# 进程内的 session 注册表。
# key 是 session_id，value 是这个 session 对应的状态对象。
_sessions: dict[str, SessionState] = {}

def set_session_meta(session_id: str, **kwargs: Any) -> None:
    s = _get_session_state(session_id)
    s.meta.update(kwargs)

def get_session_meta(session_id: str, key: str, default: Any = None) -> Any:
    return _get_session_state(session_id).meta.get(key, default)
def normalize_session_id(session_id: str | None = None) -> str:
    """
    统一解析 session_id。

    解析优先级：
    1. 调用方显式传入的 session_id
    2. 当前协程上下文里的 session_id

    这里不再允许回落到默认 session。
    多用户场景下，如果缺少 session_id 却悄悄回落，会导致不同用户串会话；
    所以现在改成 fail-fast，缺了就直接抛错。
    """
    candidate = session_id if session_id is not None else _current_session_id.get()
    if candidate is None:
        raise RuntimeError("session_id is required")

    normalized = str(candidate).strip()
    if not normalized:
        raise ValueError("session_id cannot be empty")
    return normalized


def create_session(session_id: str | None = None) -> str:
    """创建 session；如果已存在则直接复用。"""
    normalized = normalize_session_id(session_id)
    _sessions.setdefault(normalized, SessionState())
    return normalized


def has_session(session_id: str | None = None) -> bool:
    """判断某个 session 是否已经存在。"""
    return normalize_session_id(session_id) in _sessions


def delete_session(session_id: str | None = None) -> None:
    """
    删除一个 session。

    这里只清理内存中的 session 状态和订阅者集合，不负责取消 worker；
    worker 生命周期由 test.py / 后续 runtime 层统一管理。
    """
    session = _sessions.pop(normalize_session_id(session_id), None)
    if session is None:
        return
    session.subscribers.clear()


def list_sessions() -> list[str]:
    """返回当前进程里已经创建的所有 session_id。"""
    return sorted(_sessions)


def set_current_session(session_id: str | None = None) -> Token:
    """
    把当前协程上下文绑定到某个 session。

    返回的 Token 要在 finally 里交给 reset_current_session，
    这样不同协程之间的上下文不会互相污染。
    """
    normalized = normalize_session_id(session_id)
    create_session(normalized)
    return _current_session_id.set(normalized)


def reset_current_session(token: Token) -> None:
    """恢复之前的 session 上下文。"""
    _current_session_id.reset(token)


def get_current_session() -> str:
    """获取当前协程上下文绑定的 session_id。"""
    return normalize_session_id()


def _get_session_state(session_id: str | None = None) -> SessionState:
    """
    拿到某个 session 对应的 SessionState。

    这里用 setdefault，是为了让大多数调用方不需要先手动判空。
    只要 session_id 合法，就能拿到对应状态。
    """
    normalized = normalize_session_id(session_id)
    return _sessions.setdefault(normalized, SessionState())


def subscribe_session(session_id: str | None = None) -> asyncio.Queue[str]:
    """
    为某个 session 新建一个出站订阅队列。

    谁想消费这个 session 的输出流，就调用一次这个函数拿到自己的 queue，
    然后持续从 queue.get() 读取消息即可。
    """
    queue: asyncio.Queue[str] = asyncio.Queue()
    _get_session_state(session_id).subscribers.add(queue)
    return queue


def unsubscribe_session(
    queue: asyncio.Queue[str],
    session_id: str | None = None,
) -> None:
    """取消某个订阅队列与 session 的绑定。"""
    session = _sessions.get(normalize_session_id(session_id))
    if session is None:
        return
    session.subscribers.discard(queue)

def get_session_subscriber_count(session_id: str | None = None) -> int:
    """返回某个 session 当前在线订阅者数量。"""
    session = _sessions.get(normalize_session_id(session_id))
    if session is None:
        return 0
    return len(session.subscribers)


async def iter_session_messages(
    session_id: str | None = None,
) -> AsyncIterator[str]:
    """
    以 async iterator 的形式持续产出某个 session 的出站消息。

    这个接口后续很适合直接接 FastAPI 的 StreamingResponse：

        return StreamingResponse(iter_session_messages(session_id), ...)

    当前 websocket 版本虽然没直接用它，但它已经把“transport 无关”的接口准备好了。
    """
    queue = subscribe_session(session_id)
    try:
        while True:
            yield await queue.get()
    finally:
        unsubscribe_session(queue, session_id)


def _fan_out_message(message: str, session_id: str | None = None) -> None:
    """
    把一条消息广播给某个 session 的所有订阅者。

    这里广播的目标不再是 websocket client 本身，而是“订阅队列”。
    这样 transport 层可以自由替换，消息总线仍然不需要改。
    """
    session = _get_session_state(session_id)
    stale_queues: list[asyncio.Queue[str]] = []
    for queue in tuple(session.subscribers):
        try:
            # 使用 put_nowait 是因为这里做的只是进程内 fan-out，
            # 不希望一次慢消费者阻塞整个 session 的广播。
            queue.put_nowait(message)
        except Exception:
            stale_queues.append(queue)

    # 某些订阅队列如果已经不可用，就顺手移除，避免后续反复报错。
    for queue in stale_queues:
        session.subscribers.discard(queue)


def schedule_ws_broadcast(message: str, session_id: str | None = None) -> None:
    """
    兼容旧名字的“向当前 session 发布出站消息”接口。

    虽然名字里还有 ws，但语义已经变了：
    它现在不是“直接往 websocket 发”，而是“往 session 的出站总线发”。

    logger.print() 之所以不用改，就是因为它仍然调用这个函数，
    只是这个函数背后的实现已经被替换成 session 总线了。
    """
    session = _get_session_state(session_id)
    if not session.subscribers:
        # 没有订阅者时直接返回。消息不会缓存成历史记录，
        # 这是当前实现的取舍：实时流只面向当前在线消费者。
        return

    try:
        # 这里保留对事件循环存在性的判断，是为了兼容一些极端场景：
        # 如果在没有 running loop 的上下文里误调用，就直接忽略广播。
        asyncio.get_running_loop()
    except RuntimeError:
        return

    _fan_out_message(message, session_id=session_id)


def publish_session_message(
    message: str,
    session_id: str | None = None,
) -> None:
    """语义更准确的新名字；内部仍然复用旧实现。"""
    schedule_ws_broadcast(message, session_id=session_id)


async def push_client_message(
    message: Any,
    session_id: str | None = None,
) -> None:
    """
    把客户端发来的消息压入某个 session。

    入站消息会进入两套结构：
    1. raw_messages: 原始消息流
    2. event_queues: 按 type 分发后的事件队列

    这样既保留了“原始视角”，又方便 graph 节点按事件类型阻塞等待。
    """
    session = _get_session_state(session_id)
    await session.raw_messages.put(message)

    if isinstance(message, dict):
        event_type = str(message.get("type") or "").strip()
        if event_type:
            # 只有结构化事件才会进入按类型索引的队列。
            await session.event_queues[event_type].put(message)


async def receive_websocket_message(session_id: str | None = None) -> Any:
    """兼容旧接口：读取某个 session 的原始入站消息。"""
    return await _get_session_state(session_id).raw_messages.get()


async def receive_session_event(
    event_type: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """按事件类型读取某个 session 的入站消息。"""
    return await _get_session_state(session_id).event_queues[event_type].get()


async def receive_websocket_event(
    event_type: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    兼容旧名字。

    graph 节点里原本调用的是 receive_websocket_event，
    为了不大面积改调用方，这里直接转发到 receive_session_event。
    """
    return await receive_session_event(event_type, session_id=session_id)


def emit_ws_event(
    event_type: str,
    *,
    session_id: str | None = None,
    **payload: Any,
) -> None:
    """
    兼容旧名字的结构化事件发送接口。

    当前依然输出 JSON 字符串，是为了保持前端现有 onmessage 解析逻辑不变。
    """
    schedule_ws_broadcast(
        json.dumps({"type": event_type, **payload}, ensure_ascii=False),
        session_id=session_id,
    )


def _resolve_session_id_from_websocket(websocket: Any) -> str:
    """
    从 websocket 连接上解析 session_id。

    约定前端连接形式为：
        ws://host:port/?session_id=xxx

    这里不允许缺失 session_id，因为多用户模式下“自动回落默认值”会串会话。
    """
    path = getattr(websocket, "path", None)
    if path is None:
        request = getattr(websocket, "request", None)
        path = getattr(request, "path", None)

    if not path:
        raise ValueError("session_id query parameter is required")

    query = parse_qs(urlsplit(str(path)).query)
    session_id = query.get("session_id", [None])[0]
    return create_session(session_id)


def _parse_incoming_message(message: Any) -> Any:
    """
    尝试把 websocket 收到的消息解析成 JSON。

    - 如果本来就是结构化 JSON，就原样转成 dict
    - 如果不是 JSON，就包装成 {"type": "text", "text": "..."}
    """
    try:
        return json.loads(message)
    except (TypeError, json.JSONDecodeError):
        return {"type": "text", "text": str(message)}


async def _forward_messages_to_websocket(
    websocket: Any,
    queue: asyncio.Queue[str],
) -> None:
    """
    把某个 session 订阅队列里的消息持续转发到 websocket。

    注意这里 websocket 只是 transport。
    它消费的是 queue，而 queue 来自 subscribe_session(session_id)。
    """
    while True:
        message = await queue.get()
        try:
            await websocket.send(message)
        except Exception:
            # 一旦底层连接不可用，就退出转发循环，由外层 finally 清理订阅关系。
            return


async def websocket_handler(websocket) -> None:
    """
    websocket 连接处理函数。

    它做的事可以拆成三步：
    1. 从连接 URL 解析 session_id
    2. 把这个连接注册成该 session 的一个“出站订阅者”
    3. 把客户端发来的消息转成入站事件，压入该 session 的队列

    所以 websocket 在当前架构里只是“把网络连接接到 session 总线上的适配层”。
    """
    try:
        session_id = _resolve_session_id_from_websocket(websocket)
    except (RuntimeError, ValueError) as exc:
        # 1008 表示策略违规。这里用于明确告诉客户端：
        # session_id 缺失或非法，服务端拒绝建立这条连接。
        await websocket.close(code=1008, reason=str(exc))
        return

    outbound_queue = subscribe_session(session_id)
    forward_task = asyncio.create_task(
        _forward_messages_to_websocket(websocket, outbound_queue)
    )

    try:
        async for message in websocket:
            await push_client_message(
                _parse_incoming_message(message),
                session_id=session_id,
            )
    finally:
        # 不管是客户端断开、服务端取消还是内部异常，都要保证把订阅关系清理掉。
        forward_task.cancel()
        with suppress(asyncio.CancelledError):
            await forward_task
        unsubscribe_session(outbound_queue, session_id=session_id)


async def start_websocket_server(host: str = "localhost", port: int = 8765):
    """
    启动 websocket 服务。

    这里保留单例语义：如果已经启动过，就直接返回已有实例，避免重复监听端口。
    """
    global _ws_server
    import websockets

    if _ws_server is not None:
        return _ws_server

    _ws_server = await websockets.serve(websocket_handler, host, port)
    return _ws_server


async def stop_websocket_server() -> None:
    """
    停止 websocket 服务，并清理所有 session 的订阅者。

    注意这里只清理“出站订阅关系”，不会删除 session 本身，也不会取消 session worker；
    worker 生命周期仍然由 runtime 层负责。
    """
    global _ws_server

    if _ws_server is None:
        return

    _ws_server.close()
    await _ws_server.wait_closed()
    _ws_server = None

    for session in _sessions.values():
        # 连接断开后，不应该再保留旧的订阅队列引用。
        session.subscribers.clear()


__all__ = [
    "create_session",
    "delete_session",
    "emit_ws_event",
    "get_current_session",
    "has_session",
    "iter_session_messages",
    "list_sessions",
    "normalize_session_id",
    "publish_session_message",
    "push_client_message",
    "receive_session_event",
    "receive_websocket_event",
    "receive_websocket_message",
    "reset_current_session",
    "schedule_ws_broadcast",
    "set_current_session",
    "start_websocket_server",
    "stop_websocket_server",
    "subscribe_session",
    "get_session_subscriber_count",
    "unsubscribe_session",
]
