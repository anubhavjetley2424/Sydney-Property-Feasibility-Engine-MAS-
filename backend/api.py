"""
MAS Sydney – FastAPI Backend
===============================
REST API that serves dashboard data from agent outputs and provides
endpoints to trigger on-demand agent runs.

Run: uvicorn backend.api:app --reload --port 8000
"""

import sys
import os
import asyncio
import logging
from contextlib import asynccontextmanager

# Add project root to sys.path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(_project_root, ".env"))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend import data_store
from backend.scheduler import start_scheduler, stop_scheduler, get_scheduler_status

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("mas.api")


# ---------------------------------------------------------
# Lifespan: seed data + start scheduler
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed if needed, start scheduler
    if not data_store.is_seeded():
        logger.info("No data found – running seed...")
        from backend.seed_data import seed
        seed()

    start_scheduler()
    logger.info("🚀 MAS Sydney API ready")
    yield
    # Shutdown
    stop_scheduler()
    logger.info("API shutdown")


app = FastAPI(
    title="MAS Sydney Property Feasibility Engine",
    version="2.0.0",
    description="Multi-Agent System backend for Sydney residential development approvals",
    lifespan=lifespan,
)

# CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve listing images and GIS maps as static files
for static_dir in ["listing_images", "site_audits", "gis_maps"]:
    static_path = os.path.join(_project_root, static_dir)
    if os.path.isdir(static_path):
        app.mount(f"/static/{static_dir}", StaticFiles(directory=static_path), name=static_dir)


# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class RunRequest(BaseModel):
    suburb_ids: list[str] | None = None


class AgentRunRequest(BaseModel):
    agent_name: str
    task_description: str = "Analyse the target suburbs and produce a structured report."
    suburb_ids: list[str] | None = None


class DCPRunRequest(BaseModel):
    suburb_ids: list[str] | None = None
    force: bool = False


# =========================================================
# DATA ENDPOINTS
# =========================================================

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "scheduler": get_scheduler_status(),
        "data_seeded": data_store.is_seeded(),
        "suburbs_count": len(data_store.get_suburbs()),
    }


@app.get("/api/suburbs")
async def get_suburbs():
    """All suburb metadata with scores."""
    suburbs = data_store.get_suburbs()
    if not suburbs:
        raise HTTPException(404, "No suburb data. Run seed or trigger an agent run.")
    # Sort by rank or ROI score
    suburbs.sort(key=lambda s: s.get("roiScore", 0), reverse=True)
    for i, s in enumerate(suburbs):
        s["rank"] = i + 1
    return suburbs


@app.get("/api/suburbs/{suburb_id}")
async def get_suburb(suburb_id: str):
    """Single suburb metadata."""
    suburb = data_store.get_suburb(suburb_id)
    if not suburb:
        raise HTTPException(404, f"Suburb '{suburb_id}' not found")
    return suburb


@app.get("/api/suburbs/{suburb_id}/da-records")
async def get_da_records(suburb_id: str):
    """DA records for a suburb."""
    return data_store.get_da_records(suburb_id)


@app.get("/api/suburbs/{suburb_id}/properties")
async def get_properties(suburb_id: str):
    """Scouted properties for a suburb."""
    return data_store.get_properties(suburb_id)


@app.get("/api/suburbs/{suburb_id}/hot-streets")
async def get_hot_streets(suburb_id: str):
    """DA hot streets for a suburb."""
    return data_store.get_hot_streets(suburb_id)


@app.get("/api/suburbs/{suburb_id}/population")
async def get_population(suburb_id: str):
    """Population forecast data for a suburb."""
    return data_store.get_population(suburb_id)


@app.get("/api/suburbs/{suburb_id}/da-trends")
async def get_da_trends(suburb_id: str):
    """Monthly DA volume trend for a suburb."""
    return data_store.get_da_trends(suburb_id)


@app.get("/api/suburbs/{suburb_id}/economic")
async def get_economic(suburb_id: str):
    """id.com.au economic data for a suburb."""
    return data_store.get_economic(suburb_id)


# =========================================================
# AGENT RUN ENDPOINTS
# =========================================================

@app.get("/api/agent-runs")
async def get_agent_runs():
    """History of all agent runs."""
    return data_store.get_agent_runs()


@app.get("/api/scheduler")
async def scheduler_status():
    """Current scheduler status and next run times."""
    return get_scheduler_status()


@app.post("/api/run/prospect")
async def trigger_prospect(req: RunRequest):
    """Trigger prospectivity analysis (ABS + id.com.au)."""
    from backend.workflows import run_prospect_phase
    asyncio.create_task(run_prospect_phase(req.suburb_ids))
    return {"status": "started", "phase": "prospect", "suburb_ids": req.suburb_ids}


@app.post("/api/run/da-scan")
async def trigger_da_scan(req: RunRequest):
    """Trigger DA tracker scraping."""
    from backend.workflows import run_da_scan_phase
    asyncio.create_task(run_da_scan_phase(req.suburb_ids))
    return {"status": "started", "phase": "da_scan", "suburb_ids": req.suburb_ids}


@app.post("/api/run/scout")
async def trigger_scout(req: RunRequest):
    """Trigger Domain property scouting."""
    from backend.workflows import run_scout_phase
    asyncio.create_task(run_scout_phase(req.suburb_ids))
    return {"status": "started", "phase": "scout", "suburb_ids": req.suburb_ids}


@app.post("/api/run/survey")
async def trigger_survey(req: RunRequest):
    """Trigger geospatial survey."""
    from backend.workflows import run_survey_phase
    asyncio.create_task(run_survey_phase(req.suburb_ids))
    return {"status": "started", "phase": "survey", "suburb_ids": req.suburb_ids}


@app.post("/api/run/full-cycle")
async def trigger_full_cycle(req: RunRequest):
    """Trigger full agent workflow cycle."""
    from backend.workflows import run_full_cycle
    asyncio.create_task(run_full_cycle(req.suburb_ids))
    return {"status": "started", "phase": "full_cycle", "suburb_ids": req.suburb_ids}


@app.post("/api/run/dcp")
async def trigger_dcp(req: DCPRunRequest):
    """Trigger DCP PDF harvesting into Qdrant. Runs ONCE per council unless force=True."""
    from backend.workflows import run_dcp_phase
    asyncio.create_task(run_dcp_phase(req.suburb_ids, force=req.force))
    return {"status": "started", "phase": "dcp", "suburb_ids": req.suburb_ids, "force": req.force}


@app.post("/api/run/agent")
async def trigger_crewai_agent(req: AgentRunRequest):
    """Run a specific CrewAI agent (LLM-reasoned) in a background thread."""
    from backend.workflows import run_crewai_agent
    asyncio.create_task(run_crewai_agent(req.agent_name, req.task_description, req.suburb_ids))
    return {"status": "started", "agent": req.agent_name, "suburb_ids": req.suburb_ids}


# =========================================================
# DCP STATUS
# =========================================================

@app.get("/api/dcp-status")
async def dcp_status():
    """DCP harvest status per council (which ones are done, running, or pending)."""
    return data_store.get_dcp_status()


# =========================================================
# EXCEL DOWNLOAD ENDPOINTS
# =========================================================

@app.get("/api/excel/{filename}")
async def download_excel(filename: str):
    """Download a generated Excel workbook."""
    from backend.excel_store import get_excel_path
    allowed = ["prospectivity_trends.xlsx", "council_da_tracker.xlsx",
               "property_shortlist.xlsx", "dcp_summary.xlsx"]
    if filename not in allowed:
        raise HTTPException(400, f"Unknown file. Allowed: {allowed}")
    path = get_excel_path(filename)
    if not path:
        raise HTTPException(404, f"{filename} not yet generated. Run an agent phase first.")
    return FileResponse(str(path), filename=filename,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# =========================================================
# TOOL ENDPOINTS (direct tool calls for ad-hoc queries)
# =========================================================

@app.get("/api/tools/planning/{address:path}")
async def tool_planning(address: str):
    """Direct call to NSW Planning API for an address."""
    from tools import get_nsw_planning_data
    result = await get_nsw_planning_data(address)
    return result


@app.get("/api/tools/satellite")
async def tool_satellite(lat: float = Query(...), lng: float = Query(...)):
    """Direct call to satellite + VLM analysis."""
    from tools import get_satellite_and_terrain_data
    result = await get_satellite_and_terrain_data(lat, lng)
    return {"result": result}


@app.get("/api/tools/hazards")
async def tool_hazards(lat: float = Query(...), lng: float = Query(...)):
    """Direct call to NSW hazard overlays."""
    from tools import check_nsw_hazard_overlays
    import json
    result = await check_nsw_hazard_overlays(lat, lng)
    try:
        return json.loads(result) if isinstance(result, str) else result
    except Exception:
        return {"result": result}


@app.get("/api/tools/slope")
async def tool_slope(lat: float = Query(...), lng: float = Query(...)):
    """Direct call to slope analysis."""
    from tools import check_topography_and_slope
    result = await check_topography_and_slope(lat, lng)
    return {"result": result}


# =========================================================
# LLM Key Links (static)
# =========================================================

@app.get("/api/llm-links")
async def llm_links():
    return {
        "gemini": {
            "name": "Google Gemini API",
            "url": "https://aistudio.google.com/apikey",
            "description": "Get your Gemini API key for VLM site analysis and LLM summaries",
        },
        "claude": {
            "name": "Anthropic Claude API",
            "url": "https://console.anthropic.com/settings/keys",
            "description": "Get your Claude API key for advanced reasoning tasks",
        },
    }
