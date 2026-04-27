# -*- coding: utf-8 -*-
"""同步与异步操作的重试包装。

提供了两个公开函数和一种异常类型：

    run_async_with_retry    异步重试，默认通过指数退避最多尝试 3 次
    run_sync_with_retry     同步重试，同上
    RetryExhaustedError     重试次数耗尽时抛出

两种失败处理模式：

1. 不传 fallback（默认）
   耗尽重试后抛出 RetryExhaustedError，由上层决定如何处理。

2. 传入 fallback
   耗尽重试后返回 fallback 值并记录 warning 日志。适合有合理降级策略
   的场景（例如 LLM 调用失败后返回空字符串继续流程）。

两个函数均通过 retry_exceptions 参数精确控制哪些异常可重试，
避免对参数校验错误等确定性失败做无意义重试。
"""

import asyncio
from typing import Awaitable, Callable, TypeVar

from utils.logger import logger

T = TypeVar("T")
MAX_RETRY_ATTEMPTS = 3
BASE_DELAY_SECONDS = 1.0

# 哨兵：当 fallback 未传入时，表示"不降级，直接抛出异常"
_NO_FALLBACK: object = object()


class RetryExhaustedError(Exception):
    """重试次数耗尽后抛出的异常。"""

    def __init__(self, operation_name: str, attempts: int, last_error: Exception) -> None:
        self.operation_name = operation_name
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"{operation_name} 在 {attempts} 次尝试后仍然失败，最后错误: {last_error}"
        )


def _delay_seconds(attempt: int) -> float:
    """指数退避：第 2 次等 1s，第 3 次等 2s。"""
    return BASE_DELAY_SECONDS * (2 ** (attempt - 2))


async def run_async_with_retry(
    operation_name: str,
    operation: Callable[[], Awaitable[T]],
    *,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    fallback: T | object = _NO_FALLBACK,
) -> T:
    """异步重试包装器。

    耗尽重试次数后：
    - 若调用方传入了 fallback，返回 fallback 并记 warning
    - 否则抛出 RetryExhaustedError

    Example:
        result = await run_async_with_retry(
            "fetch_user",
            lambda: fetch_user(uid),
            retry_exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
        )
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            return await operation()
        except retry_exceptions as error:
            last_error = error
            logger.warning(
                f"{operation_name} 第 {attempt}/{MAX_RETRY_ATTEMPTS} 次失败: {error}"
            )
            if attempt < MAX_RETRY_ATTEMPTS:
                await asyncio.sleep(_delay_seconds(attempt))

    if fallback is not _NO_FALLBACK:
        logger.warning(
            f"{operation_name} 已耗尽 {MAX_RETRY_ATTEMPTS} 次重试，使用降级值: {fallback!r}"
        )
        return fallback  # type: ignore[return-value]

    raise RetryExhaustedError(operation_name, MAX_RETRY_ATTEMPTS, last_error)  # type: ignore[arg-type]


def run_sync_with_retry(
    operation_name: str,
    operation: Callable[[], T],
    *,
    retry_exceptions: tuple[type[Exception], ...] = (Exception,),
    fallback: T | object = _NO_FALLBACK,
) -> T:
    """同步重试包装器。

    耗尽重试次数后：
    - 若调用方传入了 fallback，返回 fallback 并记 warning
    - 否则抛出 RetryExhaustedError
    """
    import time

    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            return operation()
        except retry_exceptions as error:
            last_error = error
            logger.warning(
                f"{operation_name} 第 {attempt}/{MAX_RETRY_ATTEMPTS} 次失败: {error}"
            )
            if attempt < MAX_RETRY_ATTEMPTS:
                time.sleep(_delay_seconds(attempt))

    if fallback is not _NO_FALLBACK:
        logger.warning(
            f"{operation_name} 已耗尽 {MAX_RETRY_ATTEMPTS} 次重试，使用降级值: {fallback!r}"
        )
        return fallback  # type: ignore[return-value]

    raise RetryExhaustedError(operation_name, MAX_RETRY_ATTEMPTS, last_error)  # type: ignore[arg-type]
