"""
This module keeps console logging and can optionally mirror logs to a file based
on ``utils/config/utils.json``.
"""

import sys
from pathlib import Path
from typing import Any, Protocol, cast

from loguru import logger as _base_logger

from utils.load_config import load_json_config
from utils.websocket import schedule_ws_broadcast

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
        schedule_ws_broadcast(message)

    def printws(self, *args, sep=" ", end="\n"):
        message = f"{sep.join(map(str, args))}{end}"
        schedule_ws_broadcast(message)


logger: LoggerProtocol = cast(LoggerProtocol, _LoggerProxy(_base_logger))

__all__ = [
    "logger",
]
