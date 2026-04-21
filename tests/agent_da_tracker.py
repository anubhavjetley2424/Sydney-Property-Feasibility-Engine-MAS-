import asyncio
from tools import scrape_council_da_tracker

COUNCIL = "Parramatta"
URL = "https://datracker.cityofparramatta.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?d=thismonth&k=LodgementDate&t=DA,DAR,TA,CCP,LA,BC,CC,CD,CDP"

async def main():
    print(await scrape_council_da_tracker(COUNCIL, URL))

if __name__ == "__main__":
    asyncio.run(main())
