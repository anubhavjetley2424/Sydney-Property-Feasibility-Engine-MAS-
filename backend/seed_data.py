"""
MAS Sydney – Seed Data
========================
Populates the data store with realistic initial data so the dashboard
works immediately before the first agent run completes.

Run: python -m backend.seed_data
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend import data_store


def seed():
    """Write initial suburb data + sample DA records + properties."""

    suburbs = [
        {
            "id": "parramatta", "name": "Parramatta", "postcode": "2150", "rank": 1,
            "council": "City of Parramatta", "lga": "Parramatta",
            "roiScore": 9.2, "seifaDecile": 7,
            "medianHousePrice": 1420000, "medianUnitPrice": 650000,
            "priceGrowth5yr": 42.5, "rentalYield": 3.8, "popGrowth5yr": 11.2,
            "population": 271000, "populationForecast2036": 345000,
            "households": 98500, "medianAge": 32, "medianIncome": 82400,
            "unemployment": 4.1, "buildingApprovals": 1450,
            "immigrationRate": 8.4, "emigrationRate": 3.2, "netMigration": "+5.2%",
            "dwellings": 105000, "occupancyRate": 94.2,
            "grossRegionalProduct": "$16.2B", "localEmployment": 142000,
            "coordinates": {"lat": -33.8151, "lng": 151.0012},
            "idUrls": {
                "forecast": "https://forecast.id.com.au/parramatta",
                "economy": "https://economy.id.com.au/parramatta",
                "housing": "https://housing.id.com.au/parramatta",
                "profile": "https://profile.id.com.au/parramatta",
            },
            "dcpSummary": [
                {"rule": "Max Building Height", "value": "11m (2 storey) / 14m (3 storey) in R3/R4", "zone": "R3/R4"},
                {"rule": "Floor Space Ratio", "value": "0.75:1 (R3) / 1.2:1 (R4)", "zone": "R3/R4"},
                {"rule": "Front Setback", "value": "6m minimum", "zone": "All Residential"},
                {"rule": "Side Setback", "value": "1.2m min (single) / 1.5m (multi)", "zone": "R3"},
                {"rule": "Site Coverage", "value": "50% max", "zone": "R3"},
            ],
            "verdict": "HIGH-ROI suburb – exceptional transport links, strong population growth, and major urban renewal.",
        },
        {
            "id": "the-hills", "name": "The Hills", "postcode": "2153", "rank": 2,
            "council": "The Hills Shire Council", "lga": "The Hills Shire",
            "roiScore": 8.7, "seifaDecile": 9,
            "medianHousePrice": 1780000, "medianUnitPrice": 720000,
            "priceGrowth5yr": 38.1, "rentalYield": 3.1, "popGrowth5yr": 9.8,
            "population": 198000, "populationForecast2036": 265000,
            "households": 64500, "medianAge": 35, "medianIncome": 105000,
            "unemployment": 3.2, "buildingApprovals": 980,
            "immigrationRate": 6.2, "emigrationRate": 2.8, "netMigration": "+3.4%",
            "dwellings": 72000, "occupancyRate": 96.1,
            "grossRegionalProduct": "$12.8B", "localEmployment": 89000,
            "coordinates": {"lat": -33.7310, "lng": 150.9890},
            "idUrls": {
                "forecast": "https://forecast.id.com.au/the-hills",
                "economy": "https://economy.id.com.au/the-hills",
                "housing": "https://housing.id.com.au/the-hills",
                "profile": "https://profile.id.com.au/the-hills",
            },
            "dcpSummary": [
                {"rule": "Max Building Height", "value": "9m (2 storey)", "zone": "R2/R3"},
                {"rule": "Floor Space Ratio", "value": "0.5:1 (R2) / 0.6:1 (R3)", "zone": "R2/R3"},
                {"rule": "Front Setback", "value": "6.5m minimum", "zone": "All Residential"},
            ],
            "verdict": "PREMIUM suburb – high SEIFA, strong family demographics, metro expansion.",
        },
        {
            "id": "ryde", "name": "Ryde", "postcode": "2112", "rank": 3,
            "council": "City of Ryde", "lga": "Ryde",
            "roiScore": 8.3, "seifaDecile": 8,
            "medianHousePrice": 2150000, "medianUnitPrice": 780000,
            "priceGrowth5yr": 35.6, "rentalYield": 3.4, "popGrowth5yr": 7.5,
            "population": 135000, "populationForecast2036": 170000,
            "households": 52000, "medianAge": 34, "medianIncome": 96500,
            "unemployment": 3.8, "buildingApprovals": 720,
            "immigrationRate": 7.1, "emigrationRate": 3.5, "netMigration": "+3.6%",
            "dwellings": 57000, "occupancyRate": 95.4,
            "grossRegionalProduct": "$14.5B", "localEmployment": 95000,
            "coordinates": {"lat": -33.8152, "lng": 151.1037},
            "idUrls": {
                "forecast": "https://forecast.id.com.au/ryde",
                "economy": "https://economy.id.com.au/ryde",
                "housing": "https://housing.id.com.au/ryde",
                "profile": "https://profile.id.com.au/ryde",
            },
            "dcpSummary": [
                {"rule": "Max Building Height", "value": "9.5m (R2) / 12m (R3)", "zone": "R2/R3"},
                {"rule": "Floor Space Ratio", "value": "0.5:1 (R2) / 0.75:1 (R3)", "zone": "R2/R3"},
            ],
            "verdict": "STRONG suburb – excellent schools, tech corridor, solid capital growth.",
        },
        {
            "id": "liverpool", "name": "Liverpool", "postcode": "2170", "rank": 4,
            "council": "Liverpool City Council", "lga": "Liverpool",
            "roiScore": 7.9, "seifaDecile": 5,
            "medianHousePrice": 980000, "medianUnitPrice": 490000,
            "priceGrowth5yr": 45.2, "rentalYield": 4.2, "popGrowth5yr": 12.8,
            "population": 230000, "populationForecast2036": 340000,
            "households": 78000, "medianAge": 31, "medianIncome": 72000,
            "unemployment": 5.4, "buildingApprovals": 1100,
            "immigrationRate": 10.2, "emigrationRate": 3.8, "netMigration": "+6.4%",
            "dwellings": 84000, "occupancyRate": 93.1,
            "grossRegionalProduct": "$11.4B", "localEmployment": 68000,
            "coordinates": {"lat": -33.9200, "lng": 150.9218},
            "idUrls": {
                "forecast": "https://forecast.id.com.au/liverpool",
                "economy": "https://economy.id.com.au/liverpool",
                "housing": "https://housing.id.com.au/liverpool",
                "profile": "https://profile.id.com.au/liverpool",
            },
            "dcpSummary": [
                {"rule": "Max Building Height", "value": "9m (R2) / 11m (R3)", "zone": "R2/R3"},
                {"rule": "Floor Space Ratio", "value": "0.55:1 (R2) / 0.8:1 (R3)", "zone": "R2/R3"},
            ],
            "verdict": "HIGH-GROWTH – Aerotropolis spine, massive population influx, highest rental yields.",
        },
        {
            "id": "canterbury-bankstown", "name": "Canterbury-Bankstown", "postcode": "2200", "rank": 5,
            "council": "Canterbury-Bankstown Council", "lga": "Canterbury-Bankstown",
            "roiScore": 7.6, "seifaDecile": 4,
            "medianHousePrice": 1150000, "medianUnitPrice": 540000,
            "priceGrowth5yr": 40.3, "rentalYield": 3.9, "popGrowth5yr": 8.5,
            "population": 382000, "populationForecast2036": 445000,
            "households": 131000, "medianAge": 33, "medianIncome": 68000,
            "unemployment": 5.8, "buildingApprovals": 890,
            "immigrationRate": 7.5, "emigrationRate": 4.1, "netMigration": "+3.4%",
            "dwellings": 140000, "occupancyRate": 93.8,
            "grossRegionalProduct": "$13.1B", "localEmployment": 110000,
            "coordinates": {"lat": -33.9170, "lng": 151.0350},
            "idUrls": {
                "forecast": "https://forecast.id.com.au/canterbury-bankstown",
                "economy": "https://economy.id.com.au/canterbury-bankstown",
                "housing": "https://housing.id.com.au/canterbury-bankstown",
                "profile": "https://profile.id.com.au/canterbury-bankstown",
            },
            "dcpSummary": [
                {"rule": "Max Building Height", "value": "9m (R2) / 11.5m (R3)", "zone": "R2/R3"},
                {"rule": "Floor Space Ratio", "value": "0.5:1 (R2) / 0.7:1 (R3)", "zone": "R2/R3"},
            ],
            "verdict": "OPPORTUNITY suburb – large population, affordable entry, metro corridor expansion.",
        },
    ]

    data_store.save_suburbs(suburbs)
    print(f"[OK] Seeded {len(suburbs)} suburbs")

    # Seed some DA records, hot streets, population data per suburb
    _seed_per_suburb_data()
    print("[OK] Seed data complete")


def _seed_per_suburb_data():
    """Minimal per-suburb seed data for charts and tables."""
    import random

    streets_pool = {
        "parramatta": ["Church St", "George St", "Victoria Rd", "Albert St", "Macquarie St", "Harris St", "Smith St"],
        "the-hills": ["Showground Rd", "Old Northern Rd", "Windsor Rd", "Castle Hill Rd", "Hezlett Rd"],
        "ryde": ["Blaxland Rd", "Victoria Rd", "Lane Cove Rd", "Herring Rd", "Twin Rd"],
        "liverpool": ["Bigge St", "Moore St", "Elizabeth St", "George St", "Hume Hwy"],
        "canterbury-bankstown": ["Canterbury Rd", "Chapel Rd", "Stacey St", "Edgar St", "Wattle St"],
    }

    for sid, streets in streets_pool.items():
        # Hot streets
        hot = [{"street": s, "daCount": random.randint(3, 15), "trend": random.choice(["up", "stable", "down"])} for s in streets]
        hot.sort(key=lambda x: x["daCount"], reverse=True)
        data_store.save_hot_streets(sid, hot)

        # DA monthly trend
        months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr"]
        trend = [{"month": m, "count": random.randint(15, 55)} for m in months]
        data_store.save_da_trends(sid, trend)

        # Population forecast
        base_pop = {"parramatta": 247000, "the-hills": 175000, "ryde": 122000, "liverpool": 195000, "canterbury-bankstown": 360000}
        bp = base_pop.get(sid, 200000)
        pop = [
            {"year": 2021, "population": bp},
            {"year": 2023, "population": int(bp * 1.05)},
            {"year": 2026, "population": int(bp * 1.10)},
            {"year": 2030, "population": int(bp * 1.23)},
            {"year": 2036, "population": int(bp * 1.40)},
            {"year": 2041, "population": int(bp * 1.53)},
        ]
        data_store.save_population(sid, pop)


if __name__ == "__main__":
    seed()
