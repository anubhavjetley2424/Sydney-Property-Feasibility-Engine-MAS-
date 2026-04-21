import asyncio
from tools import autonomous_dcp_harvester

COUNCIL = "The Hills Shire Council"

async def main():
    print(await autonomous_dcp_harvester(COUNCIL))

if __name__ == "__main__":
    asyncio.run(main())
