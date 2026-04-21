import asyncio
import json
from tools import build_property_portfolio

prop = {
    "address": "28 Warrimoo Avenue St Ives NSW 2075",
    "site_area_sqm": 720,
    "zoning": "R3 Medium Density",
    "max_height": "9m",
    "floor_space_ratio": "0.7:1",
    "council": "Ku-ring-gai",
    "coordinates": {"lat": -33.73, "lng": 151.17},
    "listing_image_paths": []
}

proposal = {"proposal": {"program": {"dwelling_type": "townhouse"}}}
compliance = {"approval_likelihood": "medium", "known_non_compliances": []}

async def main():
    print(await build_property_portfolio(json.dumps(prop), json.dumps(proposal), json.dumps(compliance)))

if __name__ == "__main__":
    asyncio.run(main())
