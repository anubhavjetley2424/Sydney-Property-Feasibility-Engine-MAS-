import asyncio
from tools import (
    get_nsw_planning_data,
    check_topography_and_slope,
    check_nsw_hazard_overlays,
    get_satellite_and_terrain_data,
    generate_gis_composite_map,
)

ADDRESS = "28 Warrimoo Avenue St Ives NSW 2075"

async def main():
    planning = await get_nsw_planning_data(ADDRESS)
    print(planning)

    coords = planning.get("coordinates") or {}
    lat = float(coords.get("lat", -33.0))
    lng = float(coords.get("lng", 151.0))

    print(await check_topography_and_slope(lat, lng))
    print(await check_nsw_hazard_overlays(lat, lng))
    print(await get_satellite_and_terrain_data(lat, lng))
    print(await generate_gis_composite_map(lat, lng))

if __name__ == "__main__":
    asyncio.run(main())
