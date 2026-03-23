import os
import httpx
from crewai import Task, Crew, Process
from crewai.tools import tool

# Import the agent factory and the planning tool we already built
from agents import (
    CouncilAgents,
    nsw_planning_tool,
    site_area_tool
)

# ---------------------------------------------------------
# Lightweight Test Tool (Mapbox Satellite)
# ---------------------------------------------------------
@tool("Satellite Image Downloader")
def simple_satellite_tool(lat: float, lng: float) -> str:
    """Fetches and saves Mapbox satellite imagery locally without VLM analysis. Input: latitude, longitude floats."""
    mapbox_token = os.environ.get("MAPBOX_API_KEY")
    if not mapbox_token:
        return "ERROR: Missing MAPBOX_API_KEY environment variable."
    
    # Mapbox zoom levels go up to 22, 20 is excellent for residential rooftops
    zoom = 18
    # CRITICAL: Mapbox requires Longitude first, then Latitude!
    img_url = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lng},{lat},{zoom},0,0/640x640?access_token={mapbox_token}"
    
    try:
        # Using synchronous httpx for the test script to avoid nested event loop issues
        response = httpx.get(img_url, timeout=10.0)
        response.raise_for_status()
        
        os.makedirs("site_audits", exist_ok=True)
        filename = f"site_audits/test_satellite_{lat}_{lng}.png"
        
        with open(filename, "wb") as f:
            f.write(response.content)
            
        return f"SUCCESS: Mapbox Satellite image securely downloaded and saved to {filename}."
    except Exception as e:
        return f"ERROR downloading Mapbox image: {str(e)}"

# ---------------------------------------------------------
# Test Orchestration
# ---------------------------------------------------------
# 1. Initialize Agents
agents_factory = CouncilAgents()
scout = agents_factory.acquisition_scout()
surveyor = agents_factory.geospatial_surveyor()
designer = agents_factory.proposal_designer()
merger = agents_factory.profile_merger()
checker = agents_factory.compliance_checker()
portfolio = agents_factory.portfolio_builder()

# 2. Inject the lightweight test tool into the Surveyor
surveyor.tools = [nsw_planning_tool, simple_satellite_tool, site_area_tool]

# 3. Define Isolated Tasks
scout_task = Task(
    description="""
    Use the 'Property Scraper' tool to search the suburb 'baulkham-hills' with postcode '2153'.
    Review the deep dossiers returned. 
    Select the Top 2 properties for redevelopment based on your ROI analysis.
    Output JSON with:
    - top_properties: array of objects with address, url, and evidence_text (first 800-1200 chars from dossier).
    """,
    expected_output="JSON with top_properties array including address, url, evidence_text.",
    agent=scout
)

surveyor_task = Task(
    description="""
    Take the first property from the Scout's JSON.
    Use 'Site Area Estimator' on evidence_text to estimate site_area_sqm.
    1. Use the 'NSW Planning API' tool to get the LGA (Council), Coordinates, and Zoning.
    2. Use the 'Satellite Image Downloader' tool with those coordinates to save the image locally.
    Output JSON with:
    - address, url, site_area_sqm, zoning, max_height, floor_space_ratio, council, coordinates, constraints (array), image_path
    """,
    expected_output="JSON with property data for proposal generation.",
    agent=surveyor
)

designer_task = Task(
    description="""
    Use the Surveyor's JSON output to build a property JSON for proposal generation.
    Call 'Architecture Proposal Generator' and return the proposal JSON.
    Ensure the proposal contains explicit intentional non-compliances.
    """,
    expected_output="A proposal JSON with intentional non-compliances.",
    agent=designer
)

# Merge Task
merge_task = Task(
    description="""
    Merge Scout JSON and Surveyor JSON into a single normalized property profile.
    Use 'Property Profile Merger'.
    """,
    expected_output="Merged property JSON.",
    agent=merger
)

compliance_task = Task(
    description="""
    Use the merged property JSON and proposal JSON to run Compliance Checker.
    """,
    expected_output="Compliance assessment JSON.",
    agent=checker
)

portfolio_task = Task(
    description="""
    Use merged property JSON, proposal JSON, and compliance JSON to build local portfolio pack.
    """,
    expected_output="Portfolio output paths JSON.",
    agent=portfolio
)

# 4. Build the Mini-Crew
test_crew = Crew(
    agents=[scout, surveyor, merger, designer, checker, portfolio],
    tasks=[scout_task, surveyor_task, merge_task, designer_task, compliance_task, portfolio_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("🚀 RUNNING PHASE 1 TEST: Scout & Surveyor Pipeline (Powered by Mapbox)...")
    result = test_crew.kickoff()
    
    print("\n" + "="*50)
    print("🎯 FINAL TEST RESULTS")
    print("="*50)
    print(result)
