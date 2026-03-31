from utils.ip_utils import get_country_by_ip

import asyncio

async def main():
    print("正在查询当前 IP 归属地...")
    result = await get_country_by_ip()
    print(f"查询结果: {result}")

# 运行入口
if __name__ == "__main__":
    asyncio.run(main())