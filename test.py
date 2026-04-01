import asyncio

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.messages.ai import AIMessageChunk

from llm.service import get_model
from tools.search import search_from_baidu

from tools.registry import active_tools

from loguru import logger
tools_by_name = {
    "search_from_baidu": search_from_baidu,
}


async def stream_once(model, messages):
    full_chunk = None

    async for chunk in model.astream(messages):
        if isinstance(chunk, AIMessageChunk):
            logger.info(chunk.tool_calls)
            if chunk.content:
                print(chunk.content, end="", flush=True)

            if full_chunk is None:
                full_chunk = chunk
            else:
                full_chunk += chunk

    print()
    return full_chunk


async def main():
    model = get_model()
    model = model.bind_tools(active_tools)
    messages = [HumanMessage(content="请调用 search_from_baidu 工具搜索 2025年大事件，并基于结果给我总结。")]

    while True:
        ai_msg = await stream_once(model, messages)
        if ai_msg is None:
            break

        messages.append(ai_msg)

        if not getattr(ai_msg, "tool_calls", None):
            break

        for call in ai_msg.tool_calls:
            tool = tools_by_name[call["name"]]
            tool_result = await tool.ainvoke(call["args"])
            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=call["id"],
                )
            )


if __name__ == "__main__":
    asyncio.run(main())
