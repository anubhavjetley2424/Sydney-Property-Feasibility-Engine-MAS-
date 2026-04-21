import sys
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

# Load context from the backend workflows
from backend.workflows import run_prospect_phase

async def main():
    print("Initiating Id.com.au Suburb Scrape & Excel Export Pipeline...")
    results = await run_prospect_phase(suburb_ids=["parramatta", "ryde"])  # Running on Parramatta & Ryde for testing
    print("Agent Pipeline Output:", results)

if __name__ == "__main__":
    asyncio.run(main())
