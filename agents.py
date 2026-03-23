import os
import asyncio
import json
from crewai import Agent, LLM
from crewai.tools import tool

# Council tracker URL config
from council_trackers import SYDNEY_COUNCIL_TRACKERS

# 1. Import your custom FastMCP tools
from tools import (
    domain_investment_scraper,
    universal_page_reader, 
    ingest_pdf_from_url,
    discover_and_ingest_dcp_pdfs,
    autonomous_dcp_harvester,
    generate_architecture_proposal,
    estimate_site_area_from_text,
    merge_property_profiles,
    assess_compliance,
    build_property_portfolio,
    get_nsw_planning_data,
    query_qdrant_policy, 
    get_satellite_and_terrain_data, 
    check_topography_and_slope,  
    check_nsw_hazard_overlays,
    get_socio_economic_data,
    scrape_council_da_tracker,
    capture_domain_listing_images,
    scrape_id_data_page,
    estimate_street_median_sold,
    get_id_key_metrics,
    merge_abs_approvals_with_da_trends
)

# 2. Import the LangChain MCP adapter to load 3rd-party tools
from langchain_mcp_adapters.tools import load_mcp_tools

# ---------------------------------------------------------
# Load External Enterprise MCP Tools
# ---------------------------------------------------------
# 2026 server choices: Excel -> haris-musa/excel-mcp-server (uvx stdio, SSE fallback)
# Microsoft 365 -> Softeria/ms-365-mcp-server (npx, full Graph)
# Canva -> Official CLI MCP (npx @canva/cli@latest mcp, stdio preferred)
import logging

def _load_stdio_then_sse(label: str, stdio_cmd: list[str], sse_url: str):
    try:
        tools = load_mcp_tools(stdio_cmd[0], stdio_cmd[1:])
        print(f"{label}: MCP stdio connected.")
        logging.info("%s: MCP stdio connected.", label)
        return tools
    except Exception as e:
        print(f"{label}: stdio failed, trying SSE. Error: {e}")
        logging.info("%s: stdio failed, trying SSE. Error: %s", label, e)
        return load_mcp_tools("sse", [sse_url])

try:
    excel_mcp_tools = _load_stdio_then_sse(
        "Excel MCP",
        ["uvx", "excel-mcp-server", "stdio"],
        "http://localhost:8000/sse",
    )

    missing = [k for k in ("CLIENT_ID", "CLIENT_SECRET", "TENANT_ID") if not os.environ.get(k)]
    if missing:
        raise ValueError(
            "Microsoft 365 MCP missing env vars: " + ", ".join(missing)
        )
    m365_mcp_tools = load_mcp_tools("npx", ["@softeria/ms-365-mcp-server"])
    print("Microsoft 365 MCP connected.")
    logging.info("Microsoft 365 MCP connected.")

    canva_mcp_tools = _load_stdio_then_sse(
        "Canva MCP",
        ["npx", "@canva/cli@latest", "mcp", "stdio"],
        "http://localhost:8001/sse",
    )
except Exception as e:
    print(f"Warning: External MCP servers not found or running. {e}")
    logging.info("Warning: External MCP servers not found or running. %s", e)
    excel_mcp_tools = []
    m365_mcp_tools = []
    canva_mcp_tools = []

# ---------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------
gemini_llm = LLM(
    model="gemini/gemini-3-flash-preview", 
    api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0.1 
)

# ---------------------------------------------------------
# Dynamic Tool Wrappers (For your custom async tools)
# ---------------------------------------------------------

@tool("Socio-Economic Suburb Scanner")
def socio_economic_tool(suburb: str, postcode: str) -> str:
    """ABS Data API powered suburb scoring for high-ROI filtering."""
    return str(asyncio.run(get_socio_economic_data(suburb, postcode)))

@tool("Property Scraper")
def investment_scraper_tool(suburb: str, postcode: str) -> str:
    """Scrapes real estate listings to find redevelopment land. Input: suburb, postcode."""
    return str(asyncio.run(domain_investment_scraper(suburb, postcode)))

@tool("Listing Image Capturer")
def listing_image_tool(listing_url: str, address: str) -> str:
    """Captures full-size listing images from Domain and saves them locally."""
    return str(asyncio.run(capture_domain_listing_images(listing_url, address)))

@tool("ID Data Scraper")
def id_data_tool(url: str) -> str:
    """Scrapes id.com.au / economy.id.com.au / housing.id.com.au / profile.id.com.au pages."""
    return str(asyncio.run(scrape_id_data_page(url)))

@tool("ID Key Metrics Extractor")
def id_key_metrics_tool(url: str) -> str:
    """Extracts key metrics from id.com.au pages using heading heuristics."""
    return str(asyncio.run(get_id_key_metrics(url)))

@tool("Street Median Sold Estimator")
def street_median_tool(suburb: str, postcode: str, street: str) -> str:
    """Estimates street-level median sold price from Domain sold listings."""
    return str(asyncio.run(estimate_street_median_sold(suburb, postcode, street)))

@tool("ABS Approvals + DA Merger")
def abs_da_merge_tool(abs_csv: str, lga_2526_formatted_csv: str, da_trends_json: str) -> str:
    """Merges ABS approvals by LGA with DA trend outputs."""
    return str(asyncio.run(merge_abs_approvals_with_da_trends(abs_csv, lga_2526_formatted_csv, da_trends_json)))

@tool("Universal Browser")
def browser_tool(url: str) -> str:
    """Reads a webpage via Browserbase for deep data. Input: Full URL."""
    return str(asyncio.run(universal_page_reader(url)))

@tool("Council Tracker URL")
def council_tracker_url_tool(council_name: str, period: str = "this_month") -> str:
    """Returns the tracker URL for a council and period (this_month | last_month)."""
    council = SYDNEY_COUNCIL_TRACKERS.get(council_name)
    if not council:
        return f"ERROR: Unknown council '{council_name}'."
    url = council.get(period)
    if not url:
        return f"ERROR: No URL for period '{period}' in council '{council_name}'."
    return url

@tool("Council DA Tracker Scraper")
def council_da_tracker_scraper_tool(council_name: str, url: str) -> str:
    """Scrapes DA tracker pages with pagination and returns structured JSON."""
    return str(asyncio.run(scrape_council_da_tracker(council_name, url)))

@tool("PDF Ingestion Engine")
def pdf_tool(pdf_url: str, council_name: str) -> str:
    """Loads a Council PDF into the Vector DB. Input: PDF URL, Council Name."""
    return str(asyncio.run(ingest_pdf_from_url(pdf_url, council_name)))

@tool("Council DCP Crawler")
def dcp_crawler_tool(council_name: str) -> str:
    """Discovers and ingests council DCP PDFs into the Vector DB. Input: Council Name."""
    return str(asyncio.run(discover_and_ingest_dcp_pdfs(council_name)))

@tool("Autonomous DCP Harvester")
def dcp_harvester_tool(council_name: str) -> str:
    """Autonomously discovers and ingests council DCP PDFs into the Vector DB. Input: Council Name."""
    return str(asyncio.run(autonomous_dcp_harvester(council_name)))

@tool("Architecture Proposal Generator")
def proposal_tool(property_json: str) -> str:
    """Generates a simulated architecture proposal. Input: property JSON string."""
    return str(asyncio.run(generate_architecture_proposal(property_json)))

@tool("Site Area Estimator")
def site_area_tool(page_text: str) -> str:
    """Estimates site area from listing text. Input: page text."""
    return str(asyncio.run(estimate_site_area_from_text(page_text)))

@tool("Property Profile Merger")
def profile_merge_tool(scout_json: str, surveyor_json: str) -> str:
    """Merges scout + surveyor outputs into a normalized property JSON."""
    return str(asyncio.run(merge_property_profiles(scout_json, surveyor_json)))

@tool("Compliance Checker")
def compliance_tool(property_json: str, proposal_json: str) -> str:
    """Checks proposal vs DCP rules in Qdrant and returns assessment."""
    return str(asyncio.run(assess_compliance(property_json, proposal_json)))

@tool("Portfolio Builder")
def portfolio_tool(property_json: str, proposal_json: str, compliance_json: str) -> str:
    """Builds a local portfolio pack (JSON + Markdown)."""
    return str(asyncio.run(build_property_portfolio(property_json, proposal_json, compliance_json)))

@tool("NSW Planning API")
def nsw_planning_tool(address: str) -> str:
    """Queries NSW ArcGIS for State Zoning and Council details. Input: Full Address."""
    return str(asyncio.run(get_nsw_planning_data(address)))

@tool("Slope & Topography Analyzer")
def slope_tool(lat: float, lng: float) -> str:
    """Calculates land gradient/steepness via Google Elevation. Input: lat, lng."""
    return str(asyncio.run(check_topography_and_slope(lat, lng)))

@tool("Hazard Overlay Checker")
def hazard_tool(lat: float, lng: float) -> str:
    """Fires live ArcGIS intersection queries for Bushfire and Flood. Input: lat, lng."""
    return str(asyncio.run(check_nsw_hazard_overlays(lat, lng)))

@tool("Qdrant Policy Query")
def qdrant_query_tool(council_name: str, query: str) -> str:
    """Queries Vector DB for local DCP rules. Input: Council Name, Question."""
    return str(asyncio.run(query_qdrant_policy(council_name, query)))

@tool("Satellite Vision Inspector")
def satellite_tool(lat: float, lng: float) -> str:
    """Fetches high-res imagery and executes VLM site analysis. Input: lat, lng."""
    return str(asyncio.run(get_satellite_and_terrain_data(lat, lng)))

# ---------------------------------------------------------
# CrewAI Agent Definitions
# ---------------------------------------------------------
class CouncilAgents:
    def __init__(self):
        self.verbose = True

    def suburb_roi_analyst(self) -> Agent:
        system_instructions = (
            "Role: Suburb ROI Analyst (Data Acquisition & Scraping Module)\n"
            "Environment: Browserbase + Playwright Python API\n\n"
            "Objective:\n"
            "Navigate to the provided NSW Local Council Development Application (DA) tracker URLs. "
            "Extract a comprehensive list of all lodged applications for the specified time period, "
            "handling multi-page results autonomously. Return a clean, structured JSON array of real "
            "estate development signals.\n\n"
            "Execution Directives:\n"
            "1. Session Initialization & Navigation:\n"
            "- Launch a persistent context in Browserbase to retain session cookies.\n"
            "- Navigate to the provided URL. Wait for network idle.\n\n"
            "2. Data Extraction Protocol:\n"
            "- Locate the primary data table or list on the page.\n"
            "- Extract application_number, date_lodged, address, description, status (if visible).\n\n"
            "3. The Agentic Pagination Loop (CRITICAL):\n"
            "- Pattern A (ePathway / ASP.NET): <a> tags with href containing javascript:__doPostBack. "
            "Click next page based on active page + 1 or '>' element.\n"
            "- Pattern B (XC.Track / Masterview): buttons or links matching Next, >, >>, chevron icon.\n"
            "- After each click, wait for navigation or table re-render, then extract and append.\n"
            "- Stop when Next is missing/disabled or page content stops changing.\n\n"
            "4. Filtering & Output Formatting:\n"
            "- Tag applications containing keywords: demolition, multi-dwelling, strata, subdivision, "
            "two storey, boarding house.\n"
            "- Return JSON: {council_name, total_applications_scraped, results: [...]}\n"
        )

        return Agent(
            role="Suburb ROI Analyst (Data Acquisition & Scraping Module)",
            goal="Extract DA tracker signals and return structured JSON for ROI screening.",
            backstory=system_instructions,
            tools=[council_tracker_url_tool, council_da_tracker_scraper_tool, browser_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def socio_economic_analyst(self) -> Agent:          # ← NEW – runs FIRST
        return Agent(
            role="Socio-Economic & Growth Analyst",
            goal="Score suburbs using official ABS Data API before any scouting.",
            backstory="Identify only high-ROI suburbs (SEIFA, growth, yield). Output ranked list for the Scout.",
            tools=[socio_economic_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def acquisition_scout(self) -> Agent:
        return Agent(
            role="Lead Investment Acquisition Analyst",
            goal="Identify properties with the highest redevelopment ROI potential.",
            backstory="Use 'Property Scraper' to find large blocks. Identify the address and URL. Then use 'Listing Image Capturer' to save full-size listing photos for each target. Use 'Street Median Sold Estimator' for street-level pricing signals.",
            tools=[investment_scraper_tool, listing_image_tool, street_median_tool], 
            llm=gemini_llm,
            max_iter=3,
            verbose=self.verbose
        )

    def suburb_prospectivity_analyst(self) -> Agent:
        return Agent(
            role="Suburb Prospectivity Analyst",
            goal="Continuously collect socio-economic and DA trend signals to rank suburbs and guide scouting.",
            backstory=(
                "Operate as a long-running research agent. Use ABS data, id.com.au datasets, and council DA "
                "tracker scraping (last month + this month) to detect redevelopment hotspots by suburb and street. "
                "Summarize trends into structured notes and, when possible, push quantitative summaries into Excel "
                "via MCP for longitudinal tracking."
            ),
            tools=[
                socio_economic_tool,
                id_data_tool,
                id_key_metrics_tool,
                council_tracker_url_tool,
                council_da_tracker_scraper_tool,
                abs_da_merge_tool,
            ] + excel_mcp_tools,
            llm=gemini_llm,
            verbose=self.verbose
        )

    def finaliser(self) -> Agent:
        return Agent(
            role="Feasibility Finaliser",
            goal="Decide whether to proceed with each property based on proposal, compliance, and ROI evidence.",
            backstory=(
                "Review proposal outputs, compliance assessments, and GIS risk. Decide GO/NO-GO and "
                "summarize the decision with rationale and required follow-ups."
            ),
            tools=[qdrant_query_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def geospatial_surveyor(self) -> Agent:
        return Agent(
            role="Senior Geospatial Surveyor",
            goal="Conduct a high-intensity site audit identifying physical blockers.",
            backstory=(
                "Synthesize API, Topography, Hazard, and Satellite Vision tools into a Feasibility Report "
                "that can be consumed downstream for slide-deck creation."
            ),
            tools=[nsw_planning_tool, slope_tool, hazard_tool, satellite_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def policy_archivist(self) -> Agent:
        return Agent(
            role="Autonomous Policy Archivist",
            goal="Hunt for local Council DCP PDFs and ingest them into the knowledge base.",
            backstory="Use 'Autonomous DCP Harvester' to discover and ingest the council's DCP PDFs without hard-coded seeds.",
            tools=[dcp_harvester_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def compliance_officer(self) -> Agent:
        return Agent(
            role="Regulatory Compliance Officer",
            goal="Audit proposed designs against site data and Qdrant rules.",
            backstory="Query Qdrant for DCP rules. Cross-reference with the Surveyor's data.",
            tools=[qdrant_query_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def executive_assessor(self) -> Agent:
        return Agent(
            role="Financial Model Assessor",
            goal="Inject geospatial audit data directly into the corporate Excel feasibility model.",
            backstory="""You are an expert in financial modeling. You do not generate flat files.
            You have access to native Excel tools via MCP. You must open the master template, 
            map the terrain/hazard metrics into the correct cells, and run native formulas to calculate ROI.""",
            tools=excel_mcp_tools,  # <--- Passing the LIVE 3rd-party tools directly here!
            llm=gemini_llm,
            verbose=self.verbose
        )

    def proposal_designer(self) -> Agent:
        return Agent(
            role="Concept Architecture Lead",
            goal="Generate a council-style concept proposal tailored to each scouted property.",
            backstory="Use the Architecture Proposal Generator on the actual property data from the Scout and Surveyor.",
            tools=[proposal_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def compliance_checker(self) -> Agent:
        return Agent(
            role="Regulatory Compliance Analyst",
            goal="Assess proposal compliance against DCP rules and flag likely approval risks.",
            backstory="Use the Compliance Checker with Qdrant-ingested DCP rules.",
            tools=[compliance_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def profile_merger(self) -> Agent:
        return Agent(
            role="Property Profile Merger",
            goal="Merge Scout and Surveyor outputs into a single normalized property profile.",
            backstory="Use the Property Profile Merger tool to produce a clean JSON schema.",
            tools=[profile_merge_tool],
            llm=gemini_llm,
            verbose=self.verbose
        )

    def portfolio_builder(self) -> Agent:               # ← Canva integrated
        return Agent(
            role="Property Portfolio Builder",
            goal="Create local portfolio + autonomously generate a premium Canva slide deck.",
            backstory=(
                "After building portfolio.json and deck_manifest.json, use Canva MCP to auto-create a "
                "professional slide deck template. Each slide must include: property details, listing photos, "
                "satellite imagery, hazards/NSW planning/elevation data (as text or GIS visuals), an "
                "architecture scheme table (core features), and a compliance summary (non-approvals + followups "
                "or next steps). Use tiles or a GIS map visual for spatial data where possible. "
                "Export a polished PPTX presentation file."
            ),
            tools=[portfolio_tool] + canva_mcp_tools,
            llm=gemini_llm,
            verbose=self.verbose
        )

    def reporting_architect(self) -> Agent:
        return Agent(
            role="Lead Reporting & Distribution Architect",
            goal="Synthesize everything and push to client via M365 + optional Power Automate flow.",
            backstory="Use Microsoft Graph & Canva/Power Automate for final locked PDF and automated stakeholder delivery.",
            tools=m365_mcp_tools + canva_mcp_tools,   # + power_automate_mcp_tools if enabled
            llm=gemini_llm,
            verbose=self.verbose
        )
