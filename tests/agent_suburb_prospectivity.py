import os
import json
import asyncio
from tools import (
    get_id_key_metrics,
    scrape_council_da_tracker,
    enrich_da_with_geocode,
    aggregate_da_hotstreets,
    merge_abs_approvals_with_da_trends,
    update_prospectivity_excel,
)

ID_URLS = [
    "https://forecast.id.com.au/blacktown",
    "https://economy.id.com.au/blacktown",
    "https://housing.id.com.au/inner-west/housing-and-approvals",
    "https://profile.id.com.au/inner-west/age-by-birthplace",
]

DA_URL = "https://datracker.cityofparramatta.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?d=thismonth&k=LodgementDate&t=DA,DAR,TA,CCP,LA,BC,CC,CD,CDP"

ABS_SAMPLE = """app_month,own_sector,type_work,type_bld,lga_code,dwl,val
2025-12,1,1,110,0,10240,5157345.535
2026-01,1,1,110,0,6782,3481174.091
"""

LGA_MAP_SAMPLE = """lga_code,lga_name
10240,Parramatta
"""

async def main():
    print("ID key metrics (sample):")
    for url in ID_URLS:
        print(await get_id_key_metrics(url))

    print("\nDA tracker scrape (sample):")
    da = await scrape_council_da_tracker("Parramatta", DA_URL)
    print(da)

    print("\nDA geocode enrichment:")
    da_geo = await enrich_da_with_geocode(da if isinstance(da, str) else json.dumps(da))
    print(da_geo)

    print("\nDA hot streets:")
    print(await aggregate_da_hotstreets(da_geo))

    print("\nABS approvals merge:")
    print(await merge_abs_approvals_with_da_trends(ABS_SAMPLE, LGA_MAP_SAMPLE, da_geo))

    print("\nUpdate prospectivity Excel:")
    report = {
        "suburb_scores": [{"date": "2026-03-25", "council": "Parramatta", "suburb": "Parramatta", "roi_score": 7.8}],
        "da_trends": [{"date": "2026-03-25", "council": "Parramatta", "da_count_this_month": 12}],
        "abs_approvals": [{"month": "2026-01", "lga_code": "10240", "approvals_dwellings_total": 6782}],
        "id_metrics": [{"date": "2026-03-25", "population": 271000}],
    }
    print(await update_prospectivity_excel(json.dumps(report), "prospectivity_trends.xlsx"))

if __name__ == "__main__":
    asyncio.run(main())
