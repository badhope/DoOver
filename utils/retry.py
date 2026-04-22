# -*- coding: utf-8 -*-
"""统一重试工具模块 (Unified Retry Utilities)。
为同步与异步操作提供具备日志追踪能力的重试机制，支持失败时的优雅降级。
Attributes:
    MAX_RETRY_ATTEMPTS (int): 全局默认重试次数上限（含首次尝试），默认值为 ``3``。
Functions:
    run_async_with_retry: 异步函数重试包装器，适用于 LLM 调用、网络 IO 等场景。
    run_sync_with_retry: 同步函数重试包装器，适用于计算任务、数据解析等场景。
Example:
    异步 HTTP 请求场景::
    
        import aiohttp
        
        async def fetch_user(uid: str) -> dict:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(f"/api/users/{uid}")
                return await resp.json()
        
        user_data = await run_async_with_retry(
            operation_name="fetch_user_profile",
            operation=lambda: fetch_user("12345"),
            fallback={"error": "user_not_found"}
        )
    同步 JSON 解析场景::
    
        import json
        
        result = run_sync_with_retry(
            operation_name="parse_event_payload",
            operation=lambda: json.loads(raw_bytes),
            retry_exceptions=(json.JSONDecodeError, UnicodeDecodeError),
            fallback={}
        )
Note:
    * 被包装函数必须为无参可调用对象。若需传递参数，请使用 ``functools.partial`` 
      或 ``lambda`` 进行柯里化。
    * 当重试次数耗尽时，函数返回 ``fallback`` 值而非抛出异常。调用方应检查
      返回值以确认执行状态。
    * 异步版本捕获所有 :class:`Exception` 子类；同步版本可通过 ``retry_exceptions`` 
      参数精确控制可重试的异常类型。
    * 本模块适用于临时性失败（网络抖动、服务超时），不适用于确定性错误
      （参数校验失败、权限不足）。
See Also:
    * :mod:`tenacity`: 功能更完善的第三方重试库。
    * :mod:`asyncio`: Python 异步 I/O 标准库。
"""

from typing import Awaitable, Callable, TypeVar

from utils.logger import logger

T = TypeVar("T")
MAX_RETRY_ATTEMPTS = 3


def log_retry_failure(operation_name: str, attempt: int, error: Exception) -> None:
    logger.error(f"{operation_name} failed ({attempt}/{MAX_RETRY_ATTEMPTS}): {error}")
    if attempt < MAX_RETRY_ATTEMPTS:
        logger.info(f"{operation_name} retrying ({attempt + 1}/{MAX_RETRY_ATTEMPTS})")


async def run_async_with_retry(
    operation_name: str,
    operation: Callable[[], Awaitable[T]],
    fallback: T | None = None,
) -> T | None:
    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            return await operation()
        except Exception as error:
            log_retry_failure(operation_name, attempt, error)
    return fallback


def run_sync_with_retry(
    operation_name: str,
    operation: Callable[[], T],
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    fallback: T | None = None,
) -> T | None:
    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            return operation()
        except retry_exceptions as error:
            log_retry_failure(operation_name, attempt, error)
    return fallback
