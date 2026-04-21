"""
MAS Sydney – Agent Workflow Orchestration
==========================================
Calls the real async MCP tools from tools.py to gather live data,
then stores results in BOTH the JSON data_store AND Excel workbooks.

Workflow Phases:
  1. PROSPECT   – Socio-economic scoring + id.com.au metrics
  2. DA_SCAN    – Council DA tracker scraping + hot streets
  3. SCOUT      – Domain property scraping per suburb
  4. SURVEY     – Geospatial audit for scouted properties
  5. DCP        – Autonomous DCP PDF harvesting into Qdrant (RUN-ONCE per council)
  6. FULL_CYCLE – All phases in sequence

Scheduling Strategy (see scheduler.py):
  - DCP:     runs ONCE per council, then never again (tracked in dcp_status.json)
  - PROSPECT + DA_SCAN: daily weekdays 06:00 AEST
  - SCOUT:   weekly Monday 07:00 AEST
  - SURVEY:  weekly Monday 08:00 AEST (after scout)
  - FULL_CYCLE: on-demand via API button
"""

import sys
import os
import json
import asyncio
import logging
import re
from datetime import datetime

# Add project root to path so we can import tools.py and council_trackers.py
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from concurrent.futures import ThreadPoolExecutor

from council_trackers import SYDNEY_COUNCIL_TRACKERS
from backend import data_store
from backend import excel_store
from backend.id_data_loader import load_council_id_data, enrich_suburb_record

logger = logging.getLogger("mas.workflows")

# Thread pool for running synchronous CrewAI agents inside async context
_agent_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="crewai")

# ---------------------------------------------------------
# Suburb Configuration (maps suburb IDs to tool inputs)
# ---------------------------------------------------------
SUBURB_CONFIG = [
    {
        "id": "parramatta",
        "name": "Parramatta",
        "postcode": "2150",
        "council": "City of Parramatta",
        "council_tracker_key": "Parramatta",
        "lga": "Parramatta",
        "coordinates": {"lat": -33.8151, "lng": 151.0012},
        "idUrls": {
            "forecast": "https://forecast.id.com.au/parramatta",
            "economy": "https://economy.id.com.au/parramatta",
            "housing": "https://housing.id.com.au/parramatta",
            "profile": "https://profile.id.com.au/parramatta",
        },
    },
    {
        "id": "the-hills",
        "name": "The Hills",
        "postcode": "2153",
        "council": "The Hills Shire Council",
        "council_tracker_key": "The Hills",
        "lga": "The Hills Shire",
        "coordinates": {"lat": -33.7310, "lng": 150.9890},
        "idUrls": {
            "forecast": "https://forecast.id.com.au/the-hills",
            "economy": "https://economy.id.com.au/the-hills",
            "housing": "https://housing.id.com.au/the-hills",
            "profile": "https://profile.id.com.au/the-hills",
        },
    },
    {
        "id": "ryde",
        "name": "Ryde",
        "postcode": "2112",
        "council": "City of Ryde",
        "council_tracker_key": "Ryde",
        "lga": "Ryde",
        "coordinates": {"lat": -33.8152, "lng": 151.1037},
        "idUrls": {
            "forecast": "https://forecast.id.com.au/ryde",
            "economy": "https://economy.id.com.au/ryde",
            "housing": "https://housing.id.com.au/ryde",
            "profile": "https://profile.id.com.au/ryde",
        },
    },
    {
        "id": "liverpool",
        "name": "Liverpool",
        "postcode": "2170",
        "council": "Liverpool City Council",
        "council_tracker_key": "Liverpool",
        "lga": "Liverpool",
        "coordinates": {"lat": -33.9200, "lng": 150.9218},
        "idUrls": {
            "forecast": "https://forecast.id.com.au/liverpool",
            "economy": "https://economy.id.com.au/liverpool",
            "housing": "https://housing.id.com.au/liverpool",
            "profile": "https://profile.id.com.au/liverpool",
        },
    },
    {
        "id": "canterbury-bankstown",
        "name": "Canterbury-Bankstown",
        "postcode": "2200",
        "council": "Canterbury-Bankstown Council",
        "council_tracker_key": "Canterbury Bankstown",
        "lga": "Canterbury-Bankstown",
        "coordinates": {"lat": -33.9170, "lng": 151.0350},
        "idUrls": {
            "forecast": "https://forecast.id.com.au/canterbury-bankstown",
            "economy": "https://economy.id.com.au/canterbury-bankstown",
            "housing": "https://housing.id.com.au/canterbury-bankstown",
            "profile": "https://profile.id.com.au/canterbury-bankstown",
        },
    },
]


def _safe_json_parse(raw) -> dict | list | None:
    """Parse stringified JSON from tool output. Returns None on failure."""
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        raw = raw.strip()
        if raw.startswith("ERROR"):
            logger.warning("Tool returned error: %s", raw[:200])
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from mixed text
            for bracket in ["{", "["]:
                idx = raw.find(bracket)
                if idx >= 0:
                    try:
                        return json.loads(raw[idx:])
                    except json.JSONDecodeError:
                        continue
    return None


# ==============================================================
# PHASE 1: Prospectivity (ABS + id.com.au)
# ==============================================================
async def run_prospect_phase(suburb_ids: list[str] | None = None):
    """Score suburbs for socio-economic ROI signals."""
    from tools import get_socio_economic_data

    configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]
    suburbs_data = data_store.get_suburbs() or []
    suburb_map = {s["id"]: s for s in suburbs_data}

    # Pre-load id.com.au local Excel data per council slug
    id_com_cache: dict[str, dict] = {}

    for cfg in configs:
        sid = cfg["id"]
        logger.info("PROSPECT: %s", cfg["name"])
        try:
            # ABS socio-economic data
            abs_raw = await get_socio_economic_data(cfg["name"].lower(), cfg["postcode"])
            abs_data = _safe_json_parse(abs_raw) or {}

            # id.com.au local Excel data (loaded once per council slug, cached)
            if sid not in id_com_cache:
                id_com_cache[sid] = load_council_id_data(sid)
            id_local = id_com_cache[sid]
            if id_local:
                logger.info("PROSPECT: Loaded %d id.com metrics for %s from local Excel",
                            len([k for k in id_local if not k.startswith("_")]), sid)
            else:
                logger.info("PROSPECT: No local id.com data for %s (download Excels to backend/data/id_com/%s/)", sid, sid)

            # Build / update suburb record
            existing = suburb_map.get(sid, {})
            existing.update({
                "id": sid,
                "name": cfg["name"],
                "postcode": cfg["postcode"],
                "council": cfg["council"],
                "lga": cfg["lga"],
                "coordinates": cfg["coordinates"],
                "idUrls": cfg.get("idUrls", {}),
                "seifaDecile": abs_data.get("seifa_decile"),
                "roiScore": abs_data.get("roi_score_out_of_10"),
                "popGrowth5yr": abs_data.get("pop_growth_5yr_pct"),
                "priceGrowth5yr": abs_data.get("median_price_growth_5yr_pct"),
                "rentalYield": abs_data.get("rental_yield_pct"),
                "verdict": abs_data.get("verdict", ""),
                "lastProspectRun": datetime.now().isoformat(),
            })

            # Enrich with local id.com.au Excel data
            if id_local:
                enrich_suburb_record(existing, id_local)
                # Also persist raw id.com metrics for downstream agents
                data_store.save_economic(sid, id_local)

            suburb_map[sid] = existing

        except Exception as e:
            logger.error("PROSPECT failed for %s: %s", sid, e, exc_info=True)

    all_suburbs = list(suburb_map.values())
    data_store.save_suburbs(all_suburbs)

    # ── Excel sync ──
    try:
        excel_store.save_suburb_scores(all_suburbs)
    except Exception as e:
        logger.warning("Excel sync (prospect) failed: %s", e)

    data_store.log_agent_run("prospect", "completed", f"Processed {len(configs)} suburbs",
                             [c["id"] for c in configs])
    return {"status": "ok", "suburbs_processed": len(configs)}


# ==============================================================
# PHASE 2: DA Scanner (Council Trackers)
# ==============================================================
async def run_da_scan_phase(suburb_ids: list[str] | None = None):
    """Scrape council DA trackers and compute hot streets."""
    from tools import scrape_council_da_tracker, aggregate_da_hotstreets

    configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]

    for cfg in configs:
        sid = cfg["id"]
        tracker_key = cfg["council_tracker_key"]
        tracker = SYDNEY_COUNCIL_TRACKERS.get(tracker_key)
        if not tracker:
            logger.warning("No tracker URL for %s", tracker_key)
            continue

        url = tracker.get("this_month") or tracker.get("last_month")
        if not url:
            continue

        logger.info("DA_SCAN: %s via %s", cfg["name"], tracker_key)
        try:
            # Scrape DA tracker
            raw = await scrape_council_da_tracker(tracker_key, url)
            parsed = _safe_json_parse(raw)
            if not parsed:
                logger.warning("DA scrape returned no data for %s", sid)
                continue

            results = parsed.get("results", []) if isinstance(parsed, dict) else parsed
            data_store.save_da_records(sid, results)
            excel_store.save_da_records_excel(sid, cfg["name"], results)

            # Compute hot streets
            hot_raw = await aggregate_da_hotstreets(json.dumps(results))
            hot_parsed = _safe_json_parse(hot_raw)
            if hot_parsed and isinstance(hot_parsed, dict):
                hot_streets = hot_parsed.get("hot_streets", [])
                data_store.save_hot_streets(sid, hot_streets)
                excel_store.save_hot_streets_excel(sid, cfg["name"], hot_streets)

                # Build monthly DA trend
                monthly = hot_parsed.get("monthly_counts", {})
                trend = [{"month": k, "count": v} for k, v in sorted(monthly.items())]
                data_store.save_da_trends(sid, trend)
                excel_store.save_da_trends_excel(sid, cfg["name"], trend)

            # Update suburb building approvals count
            suburbs = data_store.get_suburbs()
            for s in suburbs:
                if s["id"] == sid:
                    s["buildingApprovals"] = len(results)
                    s["lastDAScanRun"] = datetime.now().isoformat()
                    break
            data_store.save_suburbs(suburbs)

        except Exception as e:
            logger.error("DA_SCAN failed for %s: %s", sid, e, exc_info=True)

    data_store.log_agent_run("da_scan", "completed", f"Scanned {len(configs)} councils",
                             [c["id"] for c in configs])
    return {"status": "ok", "councils_scanned": len(configs)}


# ==============================================================
# PHASE 3: Property Scout (Domain Scraping)
# ==============================================================
async def run_scout_phase(suburb_ids: list[str] | None = None):
    """Scrape Domain for investment properties."""
    from tools import domain_investment_scraper

    configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]

    for cfg in configs:
        sid = cfg["id"]
        logger.info("SCOUT: %s", cfg["name"])
        try:
            raw = await domain_investment_scraper(cfg["name"].lower(), cfg["postcode"])
            if not raw or (isinstance(raw, str) and raw.startswith("ERROR")):
                logger.warning("Scout returned error for %s: %s", sid, str(raw)[:200])
                continue

            # Parse the dossier text into structured properties
            properties = _parse_dossier(raw, cfg)
            if properties:
                data_store.save_properties(sid, properties)
                excel_store.save_properties_excel(sid, cfg["name"], properties)

            # Update suburb median price from scouted properties
            if properties:
                prices = [p["price"] for p in properties if p.get("price")]
                if prices:
                    suburbs = data_store.get_suburbs()
                    for s in suburbs:
                        if s["id"] == sid:
                            s["medianHousePrice"] = int(sum(prices) / len(prices))
                            s["lastScoutRun"] = datetime.now().isoformat()
                            break
                    data_store.save_suburbs(suburbs)

        except Exception as e:
            logger.error("SCOUT failed for %s: %s", sid, e, exc_info=True)

    data_store.log_agent_run("scout", "completed", f"Scouted {len(configs)} suburbs",
                             [c["id"] for c in configs])
    return {"status": "ok", "suburbs_scouted": len(configs)}


def _parse_dossier(dossier_text: str, cfg: dict) -> list[dict]:
    """Parse the raw dossier text from domain_investment_scraper into property dicts."""
    properties = []
    if not isinstance(dossier_text, str):
        return properties

    blocks = re.split(r"===\s*PROPERTY\s*\d+\s*===", dossier_text)
    for block in blocks[1:]:  # skip the header
        url_match = re.search(r"URL:\s*(https?://\S+)", block)
        url = url_match.group(1) if url_match else ""

        # Extract address from URL or text
        address = ""
        if url:
            parts = url.split("/")
            for p in parts:
                if re.search(r"\d{4,}", p):  # postcode-like
                    address = p.replace("-", " ").title()
                    break

        # Extract price
        price = None
        price_match = re.search(r"\$\s?([\d,]+(?:\.\d+)?)\s*(?:m|million)?", block, re.IGNORECASE)
        if price_match:
            try:
                val = price_match.group(1).replace(",", "")
                price = int(float(val))
                if price < 10000:  # probably in millions
                    price = int(price * 1_000_000)
            except (ValueError, TypeError):
                pass

        # Extract land size
        land_match = re.search(r"(\d{2,5})\s*(?:sqm|m²|m2)", block, re.IGNORECASE)
        land_size = int(land_match.group(1)) if land_match else None

        # Extract bedrooms
        bed_match = re.search(r"(\d)\s*(?:bed|bedroom)", block, re.IGNORECASE)
        bedrooms = int(bed_match.group(1)) if bed_match else None

        properties.append({
            "id": f"prop-{len(properties)+1}",
            "address": address or f"{cfg['name']} Property {len(properties)+1}",
            "price": price,
            "landSize": land_size,
            "bedrooms": bedrooms,
            "listingUrl": url,
            "suburb": cfg["name"],
            "postcode": cfg["postcode"],
            "scoutedAt": datetime.now().isoformat(),
            "rawExcerpt": block[:500],
        })

    return properties


# ==============================================================
# PHASE 4: Geospatial Survey (for scouted properties)
# ==============================================================
async def run_survey_phase(suburb_ids: list[str] | None = None):
    """Run geospatial audit on scouted properties."""
    from tools import (
        get_nsw_planning_data,
        check_topography_and_slope,
        check_nsw_hazard_overlays,
        get_satellite_and_terrain_data,
    )

    configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]

    for cfg in configs:
        sid = cfg["id"]
        properties = data_store.get_properties(sid)
        if not properties:
            logger.info("SURVEY: No properties to survey for %s", sid)
            continue

        logger.info("SURVEY: %s (%d properties)", cfg["name"], len(properties))
        for prop in properties[:3]:  # Limit to top 3 per suburb to avoid API exhaustion
            addr = prop.get("address", "")
            if not addr or prop.get("surveyCompleted"):
                continue

            try:
                # Planning data
                planning = await get_nsw_planning_data(addr)
                if isinstance(planning, dict):
                    prop["zoning"] = planning.get("zoning")
                    prop["maxHeight"] = planning.get("max_height")
                    prop["fsr"] = planning.get("floor_space_ratio")
                    prop["council"] = planning.get("council")
                    coords = planning.get("coordinates", {})
                    lat = float(coords.get("lat", cfg["coordinates"]["lat"]))
                    lng = float(coords.get("lng", cfg["coordinates"]["lng"]))
                    prop["satellite"] = {"lat": lat, "lng": lng}

                    # Slope
                    slope_result = await check_topography_and_slope(lat, lng)
                    prop["slopeAnalysis"] = slope_result if isinstance(slope_result, str) else str(slope_result)

                    # Hazards
                    hazard_result = await check_nsw_hazard_overlays(lat, lng)
                    hazard_parsed = _safe_json_parse(hazard_result)
                    prop["hazards"] = hazard_parsed or hazard_result

                    # Satellite VLM
                    sat_result = await get_satellite_and_terrain_data(lat, lng)
                    prop["vlmAnalysis"] = sat_result if isinstance(sat_result, str) else str(sat_result)

                    prop["surveyCompleted"] = True
                    prop["surveyedAt"] = datetime.now().isoformat()

            except Exception as e:
                logger.error("SURVEY failed for property %s: %s", addr, e)

        data_store.save_properties(sid, properties)
        excel_store.save_properties_excel(sid, cfg["name"], properties)

    data_store.log_agent_run("survey", "completed", f"Surveyed properties in {len(configs)} suburbs",
                             [c["id"] for c in configs])
    return {"status": "ok", "suburbs_surveyed": len(configs)}


# ==============================================================
# PHASE 5: DCP Harvester (RUN-ONCE per council)
# ==============================================================
async def run_dcp_phase(suburb_ids: list[str] | None = None, force: bool = False):
    """
    Harvest DCP PDFs into Qdrant for each council that hasn't been processed.
    Only runs once per council unless force=True.
    """
    from tools import autonomous_dcp_harvester

    configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]
    harvested = 0
    skipped = 0

    for cfg in configs:
        council = cfg["council"]
        sid = cfg["id"]

        # Skip if already harvested (run-once logic)
        if not force and data_store.is_dcp_harvested(council):
            logger.info("DCP: Skipping %s — already harvested", council)
            skipped += 1
            continue

        logger.info("DCP: Harvesting %s", council)
        data_store.save_dcp_status(council, "running")
        try:
            result = await autonomous_dcp_harvester(council)
            parsed = _safe_json_parse(result)
            docs = 0
            details = ""
            if parsed and isinstance(parsed, dict):
                docs = parsed.get("total_ingested", 0)
                details = parsed.get("summary", str(result)[:500])
            elif isinstance(result, str):
                details = result[:500]

            data_store.save_dcp_status(council, "completed", docs, details)
            excel_store.save_dcp_harvest_log(council, "completed", docs, details)
            harvested += 1

        except Exception as e:
            logger.error("DCP failed for %s: %s", council, e, exc_info=True)
            data_store.save_dcp_status(council, "failed", 0, str(e)[:500])
            excel_store.save_dcp_harvest_log(council, "failed", 0, str(e)[:500])

    data_store.log_agent_run("dcp", "completed",
                             f"Harvested {harvested}, skipped {skipped} (already done)",
                             [c["id"] for c in configs])
    return {"status": "ok", "harvested": harvested, "skipped": skipped}


# ==============================================================
# FULL CYCLE (all phases in sequence)
# ==============================================================
async def run_full_cycle(suburb_ids: list[str] | None = None):
    """Execute all phases in sequence: DCP → Prospect → DA Scan → Scout → Survey."""
    logger.info("=== FULL CYCLE START ===")
    data_store.log_agent_run("full_cycle", "started", "", suburb_ids or [c["id"] for c in SUBURB_CONFIG])

    results = {}
    try:
        # DCP first (will skip councils already harvested)
        results["dcp"] = await run_dcp_phase(suburb_ids)
        results["prospect"] = await run_prospect_phase(suburb_ids)
        results["da_scan"] = await run_da_scan_phase(suburb_ids)
        results["scout"] = await run_scout_phase(suburb_ids)
        results["survey"] = await run_survey_phase(suburb_ids)
        data_store.log_agent_run("full_cycle", "completed", json.dumps(results, default=str))
    except Exception as e:
        logger.error("FULL CYCLE failed: %s", e, exc_info=True)
        data_store.log_agent_run("full_cycle", "failed", str(e))
        results["error"] = str(e)

    logger.info("=== FULL CYCLE END ===")
    return results


# ==============================================================
# CrewAI AGENT BRIDGE
# ==============================================================
# CrewAI agents use synchronous asyncio.run() internally, which
# clashes with FastAPI's running event loop. We bridge this by
# running CrewAI tasks in a thread pool via asyncio.to_thread.
# ==============================================================

async def run_crewai_agent(agent_name: str, task_description: str, suburb_ids: list[str] | None = None):
    """
    Run a named CrewAI agent from agents.py in a background thread.
    This allows the LLM to reason about tool usage rather than
    following the deterministic workflow.

    Supported agents:
      - suburb_roi_analyst
      - socio_economic_analyst
      - acquisition_scout
      - suburb_prospectivity_analyst
      - policy_archivist
      - geospatial_surveyor
      - compliance_officer
      - proposal_designer
      - portfolio_builder
    """
    from crewai import Task, Crew

    loop = asyncio.get_event_loop()

    def _run_in_thread():
        from agents import CouncilAgents
        agents = CouncilAgents()

        agent_map = {
            "suburb_roi_analyst": agents.suburb_roi_analyst,
            "socio_economic_analyst": agents.socio_economic_analyst,
            "acquisition_scout": agents.acquisition_scout,
            "suburb_prospectivity_analyst": agents.suburb_prospectivity_analyst,
            "policy_archivist": agents.policy_archivist,
            "geospatial_surveyor": agents.geospatial_surveyor,
            "compliance_officer": agents.compliance_officer,
            "proposal_designer": agents.proposal_designer,
            "portfolio_builder": agents.portfolio_builder,
        }

        factory = agent_map.get(agent_name)
        if not factory:
            return {"error": f"Unknown agent: {agent_name}. Available: {list(agent_map.keys())}"}

        agent = factory()

        # Build context from suburb config
        configs = SUBURB_CONFIG if not suburb_ids else [c for c in SUBURB_CONFIG if c["id"] in suburb_ids]
        context = json.dumps({
            "suburbs": [{"id": c["id"], "name": c["name"], "postcode": c["postcode"],
                         "council": c["council"]} for c in configs],
            "task": task_description,
        }, indent=2)

        task = Task(
            description=f"{task_description}\n\nContext:\n{context}",
            expected_output="Structured JSON or detailed analysis report.",
            agent=agent,
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()
        return {"status": "ok", "agent": agent_name, "output": str(result)}

    data_store.log_agent_run(f"crewai_{agent_name}", "started", task_description, suburb_ids or [])
    try:
        result = await loop.run_in_executor(_agent_pool, _run_in_thread)
        data_store.log_agent_run(f"crewai_{agent_name}", "completed",
                                 json.dumps(result, default=str)[:500])
        return result
    except Exception as e:
        logger.error("CrewAI agent %s failed: %s", agent_name, e, exc_info=True)
        data_store.log_agent_run(f"crewai_{agent_name}", "failed", str(e))
        return {"error": str(e)}
