import asyncio
import json
from tools import generate_architecture_proposal

sample_property = {
    "address": "28 Warrimoo Avenue St Ives NSW 2075",
    "site_area_sqm": 720,
    "zoning": "R3 Medium Density",
    "max_height": "9m",
    "floor_space_ratio": "0.7:1",
    "constraints": ["bushfire overlay"]
}

async def main():
    print(await generate_architecture_proposal(json.dumps(sample_property)))

if __name__ == "__main__":
    asyncio.run(main())
