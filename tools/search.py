import aiohttp
from loguru import logger
from pathlib import Path
from langchain.tools import tool 
import json
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
@tool
async def search_from_baidu(query: str) -> str:
    """
    This tool must be invoked whenever a network search is required. 
    It allows the model to query the Baidu search engine by sending a request with a query string to the Baidu Search API.
    The tool then returns the relevant search results, which the model can process or use for subsequent generation tasks that involve external search data.
    """
    result = await baidu_qianfan_web_search(content=query)
    logger.info(f"Baidu Search Result: {json.dumps(result, ensure_ascii=False)}")
    return json.dumps(result, ensure_ascii=False)