import asyncio
import json
from typing import Any

_ws_clients = set()
_ws_server = None
_ws_message_queue = asyncio.Queue()


async def _broadcast_ws_message(message: str) -> None:
    if not _ws_clients:
        return

    stale_clients = []
    for client in tuple(_ws_clients):
        try:
            await client.send(message)
        except Exception:
            stale_clients.append(client)

    for client in stale_clients:
        _ws_clients.discard(client)


def schedule_ws_broadcast(message: str) -> None:
    if not _ws_clients:
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    loop.create_task(_broadcast_ws_message(message))


async def websocket_handler(websocket) -> None:
    _ws_clients.add(websocket)
    try:
        async for message in websocket:
            try:
                parsed_message = json.loads(message)
            except (TypeError, json.JSONDecodeError):
                parsed_message = {"type": "text", "text": str(message)}
            await _ws_message_queue.put(parsed_message)
    finally:
        _ws_clients.discard(websocket)


async def start_websocket_server(host: str = "localhost", port: int = 8765):
    global _ws_server
    import websockets

    if _ws_server is not None:
        return _ws_server

    _ws_server = await websockets.serve(websocket_handler, host, port)
    return _ws_server


async def stop_websocket_server() -> None:
    global _ws_server

    if _ws_server is None:
        return

    _ws_server.close()
    await _ws_server.wait_closed()
    _ws_server = None
    _ws_clients.clear()


async def receive_websocket_message() -> Any:
    return await _ws_message_queue.get()


async def receive_websocket_event(event_type: str) -> dict[str, Any]:
    while True:
        event = await _ws_message_queue.get()
        if isinstance(event, dict) and event.get("type") == event_type:
            return event


def emit_ws_event(event_type: str, **payload: Any) -> None:
    schedule_ws_broadcast(
        json.dumps({"type": event_type, **payload}, ensure_ascii=False)
    )


__all__ = [
    "emit_ws_event",
    "receive_websocket_event",
    "receive_websocket_message",
    "schedule_ws_broadcast",
    "start_websocket_server",
    "stop_websocket_server",
]
