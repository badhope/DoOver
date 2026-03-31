"""Moonshot/Kimi chat provider built on the OpenAI-compatible API."""

from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Sequence

from openai import AsyncOpenAI, OpenAI
from pydantic import Field, SecretStr

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.messages.ai import (
    InputTokenDetails,
    OutputTokenDetails,
    UsageMetadata,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.utils import convert_to_secret_str, get_from_dict_or_env, pre_init

MOONSHOT_SERVICE_URL_BASE = "https://api.moonshot.cn/v1"


class MoonshotLLM(BaseChatModel):
    api_key: Optional[SecretStr] = Field(default=None)
    base_url: str = MOONSHOT_SERVICE_URL_BASE
    model: str = "moonshot-v1-8k"
    temperature: float = 1.0
    max_tokens: int | None = None
    stream_usage: bool = True

    client: Any = None
    async_client: Any = None

    def __init__(
        self,
        *,
        model: str = "moonshot-v1-8k",
        api_key: str | SecretStr | None = None,
        base_url: str = MOONSHOT_SERVICE_URL_BASE,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        stream_usage: bool = True,
        model_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            stream_usage=stream_usage,
            **kwargs,
        )

    @property
    def model_name(self) -> str:
        return self.model

    @pre_init
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        api_key = convert_to_secret_str(
            get_from_dict_or_env(values, "api_key", "MOONSHOT_API_KEY")
        )
        base_url = values.get("base_url", MOONSHOT_SERVICE_URL_BASE)
        values["api_key"] = api_key
        values["client"] = OpenAI(
            api_key=api_key.get_secret_value(),
            base_url=base_url,
        )
        values["async_client"] = AsyncOpenAI(
            api_key=api_key.get_secret_value(),
            base_url=base_url,
        )
        return values

    @property
    def _llm_type(self) -> str:
        return "moonshot-chat"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def _default_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def _create_usage_metadata(self, usage: Any) -> UsageMetadata | None:
        if usage is None:
            return None
        usage_dict = usage.model_dump() if hasattr(usage, "model_dump") else dict(usage)
        input_tokens = usage_dict.get("prompt_tokens") or 0
        output_tokens = usage_dict.get("completion_tokens") or 0
        total_tokens = usage_dict.get("total_tokens") or (input_tokens + output_tokens)
        return UsageMetadata(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_token_details=InputTokenDetails(),
            output_token_details=OutputTokenDetails(),
        )

    def _convert_messages(self, messages: Sequence[BaseMessage]) -> List[Dict[str, Any]]:
        payload_messages: List[Dict[str, Any]] = []
        for message in messages:
            role = "assistant"
            if message.type == "human":
                role = "user"
            elif message.type == "system":
                role = "system"
            elif message.type == "ai":
                role = "assistant"
            else:
                role = message.type
            payload_messages.append({"role": role, "content": message.content})
        return payload_messages

    def _build_request(
        self,
        messages: Sequence[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        request: Dict[str, Any] = {
            **self._default_params(),
            "messages": self._convert_messages(messages),
        }
        if stop:
            request["stop"] = stop
        request.update(kwargs)
        return {k: v for k, v in request.items() if v is not None}

    def _create_chat_result(self, response: Any) -> ChatResult:
        text = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else None
        message = AIMessage(
            content=text,
            response_metadata={
                "token_usage": usage,
                "model": response.model,
            },
            usage_metadata=self._create_usage_metadata(response.usage),
        )
        return ChatResult(generations=[ChatGeneration(message=message)])

    def _build_stream_text_chunk(
        self,
        *,
        text: str,
        message_id: str | None = None,
        include_message_id: bool = False,
    ) -> AIMessageChunk:
        block: Dict[str, Any] = {"type": "text", "text": text, "index": 0}
        if include_message_id and message_id:
            block["id"] = message_id
        return AIMessageChunk(
            content=[block],
            response_metadata={"model_provider": "openai"},
        )

    def _build_final_stream_chunk(
        self,
        *,
        chunk_id: str | None,
        model_name: str,
        final_usage: Any,
    ) -> AIMessageChunk:
        return AIMessageChunk(
            content=[],
            id=chunk_id,
            response_metadata={
                "model": model_name,
                "model_name": model_name,
                "model_provider": "openai",
            },
            usage_metadata=self._create_usage_metadata(final_usage),
            chunk_position="last",
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        request = self._build_request(messages, stop=stop, **kwargs)
        response = self.client.chat.completions.create(**request)
        text = response.choices[0].message.content or ""
        if run_manager and text:
            run_manager.on_llm_new_token(text)
        return self._create_chat_result(response)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        request = self._build_request(messages, stop=stop, **kwargs)
        if self.stream_usage and "stream_options" not in request:
            request["stream_options"] = {"include_usage": True}
        response = self.client.chat.completions.create(stream=True, **request)
        chunk_id = None
        model_name = self.model_name
        final_usage = None
        sent_any_text = False
        for chunk in response:
            if getattr(chunk, "id", None):
                chunk_id = chunk.id
            if getattr(chunk, "model", None):
                model_name = chunk.model
            if getattr(chunk, "usage", None):
                final_usage = chunk.usage
            if chunk.choices:
                choice = chunk.choices[0]
                message_id = getattr(choice.delta, "id", None)
                token = chunk.choices[0].delta.content or ""
            else:
                message_id = None
                token = ""
            if not token:
                continue
            sent_any_text = True
            if run_manager:
                run_manager.on_llm_new_token(token)
            yield ChatGenerationChunk(
                message=self._build_stream_text_chunk(text=token)
            )
        if sent_any_text:
            yield ChatGenerationChunk(
                message=self._build_stream_text_chunk(
                    text="",
                    message_id=message_id if "message_id" in locals() else None, # type: ignore
                    include_message_id=True,
                )
            )
        yield ChatGenerationChunk(
            message=self._build_final_stream_chunk(
                chunk_id=chunk_id,
                model_name=model_name,
                final_usage=final_usage,
            )
        )

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        request = self._build_request(messages, stop=stop, **kwargs)
        response = await self.async_client.chat.completions.create(**request)
        text = response.choices[0].message.content or ""
        if run_manager and text:
            await run_manager.on_llm_new_token(text)
        return self._create_chat_result(response)

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        request = self._build_request(messages, stop=stop, **kwargs)
        if self.stream_usage and "stream_options" not in request:
            request["stream_options"] = {"include_usage": True}
        response = await self.async_client.chat.completions.create(
            stream=True, **request
        )
        chunk_id = None
        model_name = self.model_name
        final_usage = None
        sent_any_text = False
        async for chunk in response:
            if getattr(chunk, "id", None):
                chunk_id = chunk.id
            if getattr(chunk, "model", None):
                model_name = chunk.model
            if getattr(chunk, "usage", None):
                final_usage = chunk.usage
            if chunk.choices:
                choice = chunk.choices[0]
                message_id = getattr(choice.delta, "id", None)
                token = chunk.choices[0].delta.content or ""
            else:
                message_id = None
                token = ""
            if not token:
                continue
            sent_any_text = True
            if run_manager:
                await run_manager.on_llm_new_token(token)
            yield ChatGenerationChunk(
                message=self._build_stream_text_chunk(text=token)
            )
        if sent_any_text:
            yield ChatGenerationChunk(
                message=self._build_stream_text_chunk(
                    text="",
                    message_id=message_id if "message_id" in locals() else None, # type: ignore
                    include_message_id=True,
                )
            )
        yield ChatGenerationChunk(
            message=self._build_final_stream_chunk(
                chunk_id=chunk_id,
                model_name=model_name,
                final_usage=final_usage,
            )
        )


def create_moonshot_llm(
    model: str,
    api_key: str,
    base_url: str = MOONSHOT_SERVICE_URL_BASE,
    **kwargs: Any,
) -> MoonshotLLM:
    return MoonshotLLM(
        model=model,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )
