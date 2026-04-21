import asyncio
from tools import query_qdrant_policy

COUNCIL = "The Hills Shire Council"
QUERY = "setbacks and floor space ratio"

async def main():
    print(await query_qdrant_policy(COUNCIL, QUERY))

if __name__ == "__main__":
    asyncio.run(main())
