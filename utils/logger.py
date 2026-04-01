"""
This module keeps console logging and can optionally mirror logs to a file based
on ``utils/config/utils.json``.

- Standard log methods such as ``logger.info(...)`` always write to the console,
  and also write to ``logs/doover.log`` when ``logger.is_to_file`` is enabled.
- ``logger.print(...)`` follows the same console/file behavior and also broadcasts
  to WebSocket clients.
- ``logger.printws(...)`` broadcasts to WebSocket clients only.

Usage:
    from utils.logger import logger, start_websocket_server, stop_websocket_server

    await start_websocket_server("localhost", 8765)
    logger.info("hello world")
    logger.print("hello world")
    logger.printws("websocket only")
    await stop_websocket_server()
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Protocol, cast

from loguru import logger as _base_logger
from utils.load_config import load_json_config

_ws_clients = set()
_ws_server = None
_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "utils.json"
_logger_config = load_json_config(_CONFIG_PATH).get("logger", {})
_is_to_file = bool(_logger_config.get("is_to_file", False))

_base_logger.remove()
_base_logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
)
if _is_to_file:
    _base_logger.add(
        "logs/doover.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        encoding="utf-8",
    )


class LoggerProtocol(Protocol):
    def debug(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def info(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def warning(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def error(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def critical(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def exception(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def success(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def trace(self, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def log(self, level: Any, message: Any, *args: Any, **kwargs: Any) -> Any: ...
    def bind(self, **kwargs: Any) -> Any: ...
    def opt(self, *args: Any, **kwargs: Any) -> Any: ...
    def add(self, *args: Any, **kwargs: Any) -> Any: ...
    def remove(self, *args: Any, **kwargs: Any) -> Any: ...
    def print(self, *args: Any, sep: str = " ", end: str = "\n") -> None: ...
    def printws(self, *args: Any, sep: str = " ", end: str = "\n") -> None: ...


class _LoggerProxy:
    def __init__(self, base_logger):
        self._base_logger = base_logger

    def __getattr__(self, name):
        return getattr(self._base_logger, name)

    def print(self, *args, sep=" ", end="\n"):
        message = f"{sep.join(map(str, args))}{end}"
        self._base_logger.opt(raw=True).info(message)
        _schedule_ws_broadcast(message)

    def printws(self, *args, sep=" ", end="\n"):
        message = f"{sep.join(map(str, args))}{end}"
        _schedule_ws_broadcast(message)


async def _broadcast_ws_message(message):
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


def _schedule_ws_broadcast(message):
    if not _ws_clients:
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    loop.create_task(_broadcast_ws_message(message))


async def websocket_handler(websocket):
    _ws_clients.add(websocket)
    try:
        async for message in websocket:
            await websocket.send(message)
    finally:
        _ws_clients.discard(websocket)


async def start_websocket_server(host="localhost", port=8765):
    global _ws_server
    import websockets

    if _ws_server is not None:
        return _ws_server

    _ws_server = await websockets.serve(websocket_handler, host, port)
    return _ws_server


async def stop_websocket_server():
    global _ws_server

    if _ws_server is None:
        return

    _ws_server.close()
    await _ws_server.wait_closed()
    _ws_server = None
    _ws_clients.clear()


logger: LoggerProtocol = cast(LoggerProtocol, _LoggerProxy(_base_logger))

__all__ = ["logger", "start_websocket_server", "stop_websocket_server"]
