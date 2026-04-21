import asyncio
from tools import domain_investment_scraper, capture_domain_listing_images, estimate_street_median_sold

SUBURB = "parramatta"
POSTCODE = "2150"
STREET = "Church Street"

async def main():
    print(await domain_investment_scraper(SUBURB, POSTCODE))
    # Example: update with a real listing URL from the output above
    sample_url = "https://www.domain.com.au/"
    if sample_url == "https://www.domain.com.au/":
        print("SKIP: Set sample_url to a real listing URL before running image capture.")
    else:
        print(await capture_domain_listing_images(sample_url, f\"{STREET}, {SUBURB.upper()}\"))
    print(await estimate_street_median_sold(SUBURB, POSTCODE, STREET))

if __name__ == "__main__":
    asyncio.run(main())
