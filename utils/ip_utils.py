import aiohttp
from loguru import logger

async def get_country_by_ip():
    # 定义 URL
    url = 'http://ip-api.com/json/'
    
    # 创建会话并发送请求
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                # 检查 HTTP 状态码
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        return {
                            "国家": data.get('country'),
                            "城市": data.get('city'),
                            "运营商": data.get('isp')
                        }
                    else:
                        logger.warning(f"API 返回错误: {data.get('message')}")
                        return {"位置": "未知"}
                else:
                    logger.error(f"HTTP 请求失败，状态码: {response.status}")
                    return {"位置": "未知"}
                    
        except aiohttp.ClientError as e:
            logger.error(f"网络连接错误: {e}")
            return {"位置": "未知"}
        except Exception as e:
            logger.error(f"发生未知异常: {e}")
            return {"位置": "未知"}