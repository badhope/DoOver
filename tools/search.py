import asyncio

import aiohttp
from utils.logger import logger
from pathlib import Path
from langchain.tools import tool 
import json

from tools.args_schemas.serach_args_schemas import search_from_tavily_field_info
from utils.load_config import load_json_config


CONFIG_PATH = Path(__file__).resolve().parent / "config" / "tools.json"
config = load_json_config(CONFIG_PATH)

async def baidu_qianfan_web_search(content: str, api_key: str | None = None):
    """
    使用 aiohttp 调用百度千帆 AI 搜索 (POST /v2/ai_search/web_search)
    
    :param api_key: 百度的 API Key
    """
    baidu_config = config.get("search", {}).get("baidu", {})
    api_key = api_key or baidu_config.get("api_key")
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {
                "content": f"{content}",
                "role": "user"
            }
        ],
        "search_source": "baidu_search_v2",
        "search_recency_filter": "year"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                # 获取响应状态码
                status = response.status
                
                if status == 200:
                    # 解析 JSON 响应
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Request failed with status {status}: {error_text}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"AIOHTTP Client Error: {e}")
            raise
        except Exception as e:
            logger.error(f"General Error: {e}")
            raise


async def tavily_web_search(query: str, api_key: str | None = None):
    """
    这个是使用curl进行对接tavily的toolSearch
    :param query: 这个是关键词 / 用户输入的内容
    :param api_key: 这个是对应的API密钥 / 一般不会传入
    :return: 返回jsonStr给LLM
    """
    tavily_config = config.get("search", {}).get("tavily", {})
    api_key = api_key or tavily_config.get("api_key")
    url = tavily_config.get("base_url")
    print(url)
    print(api_key)



    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "auto_parameters": False,
        "topic": "general",
        "search_depth": "basic",
        "chunks_per_source": 3,
        "max_results": 1, #表示最高一条
        "time_range": "y"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as response:
                # 获取响应状态码
                status = response.status

                if status == 200:
                    # 解析 JSON 响应
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"Request failed with status {status}: {error_text}")

        except aiohttp.ClientError as e:
            logger.error(f"AIOHTTP Client Error: {e}")
            raise
        except Exception as e:
            logger.error(f"General Error: {e}")
            raise

@tool
async def search_from_baidu(query: str) -> str:
    """
    This tool must be invoked whenever a network search is required. 
    It allows the model to query the Baidu search engine by sending a request with a query string to the Baidu Search API.
    The tool then returns the relevant search results, which the model can process or use for subsequent generation tasks that involve external search data.
    """
    result = await baidu_qianfan_web_search(content=query)
    result = result["references"]
    logger.print(f"Baidu Search Result: {json.dumps(result, ensure_ascii=False)}")
    return json.dumps(result, ensure_ascii=False)

@tool(name_or_callable="web_search",
      description= "This tool must be invoked whenever a network search is required."
                   "It allows the model to query the Tavily search engine by sending a request with a query string to the Tavily Search API."
                   "The tool then returns relevant, up-to-date search results—including authoritative sources and real-time information—which the model can process or use for subsequent generation tasks that rely on external, factual data.",
      args_schema=search_from_tavily_field_info,
      return_direct=False)
async def search_from_tavily(query: str,tavily_api_key)->str:
    result =  await tavily_web_search(query,tavily_api_key)
    logger.info(f"Tavily Search Result: {json.dumps(result, ensure_ascii=False)}")
    return json.dumps(result, ensure_ascii=False)
