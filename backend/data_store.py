"""
MAS Sydney – JSON File-Based Data Store
========================================
Stores and retrieves agent outputs as JSON files so the dashboard API can
serve real data without re-running agents on every request.

Directory layout:
  backend/data/
    suburbs.json          – suburb metadata + scores
    da_records/
      parramatta.json     – DA records per suburb
      the-hills.json
      ...
    properties/
      parramatta.json     – scouted properties per suburb
      ...
    hot_streets/
      parramatta.json
      ...
    population/
      parramatta.json
      ...
    da_trends/
      parramatta.json     – monthly DA volume
      ...
    agent_runs.json       – log of all agent run timestamps + status
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger("mas.data_store")

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------
# Ensure directory structure
# ---------------------------------------------------------
SUBDIRS = [
    "da_records", "properties", "hot_streets",
    "population", "da_trends", "economic",
]

def _ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (DATA_DIR / sub).mkdir(exist_ok=True)

_ensure_dirs()


# ---------------------------------------------------------
# Generic Read / Write
# ---------------------------------------------------------
def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to read %s: %s", path, e)
        return None


def _write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Wrote %s (%d bytes)", path, path.stat().st_size)


# ---------------------------------------------------------
# Suburb Master Data
# ---------------------------------------------------------
def get_suburbs() -> list[dict]:
    data = _read_json(DATA_DIR / "suburbs.json")
    return data if isinstance(data, list) else []


def save_suburbs(suburbs: list[dict]):
    _write_json(DATA_DIR / "suburbs.json", suburbs)


def get_suburb(suburb_id: str) -> dict | None:
    for s in get_suburbs():
        if s.get("id") == suburb_id:
            return s
    return None


# ---------------------------------------------------------
# Per-Suburb Collections
# ---------------------------------------------------------
def _suburb_path(collection: str, suburb_id: str) -> Path:
    safe = suburb_id.replace(" ", "-").lower()
    return DATA_DIR / collection / f"{safe}.json"


def get_da_records(suburb_id: str) -> list[dict]:
    return _read_json(_suburb_path("da_records", suburb_id)) or []


def save_da_records(suburb_id: str, records: list[dict]):
    _write_json(_suburb_path("da_records", suburb_id), records)


def get_properties(suburb_id: str) -> list[dict]:
    return _read_json(_suburb_path("properties", suburb_id)) or []


def save_properties(suburb_id: str, props: list[dict]):
    _write_json(_suburb_path("properties", suburb_id), props)


def get_hot_streets(suburb_id: str) -> list[dict]:
    return _read_json(_suburb_path("hot_streets", suburb_id)) or []


def save_hot_streets(suburb_id: str, streets: list[dict]):
    _write_json(_suburb_path("hot_streets", suburb_id), streets)


def get_population(suburb_id: str) -> list[dict]:
    return _read_json(_suburb_path("population", suburb_id)) or []


def save_population(suburb_id: str, data: list[dict]):
    _write_json(_suburb_path("population", suburb_id), data)


def get_da_trends(suburb_id: str) -> list[dict]:
    return _read_json(_suburb_path("da_trends", suburb_id)) or []


def save_da_trends(suburb_id: str, data: list[dict]):
    _write_json(_suburb_path("da_trends", suburb_id), data)


def get_economic(suburb_id: str) -> dict:
    return _read_json(_suburb_path("economic", suburb_id)) or {}


def save_economic(suburb_id: str, data: dict):
    _write_json(_suburb_path("economic", suburb_id), data)


# ---------------------------------------------------------
# Agent Run Log
# ---------------------------------------------------------
def get_agent_runs() -> list[dict]:
    return _read_json(DATA_DIR / "agent_runs.json") or []


def log_agent_run(run_type: str, status: str, details: str = "", suburbs: list[str] | None = None):
    runs = get_agent_runs()
    runs.append({
        "timestamp": datetime.now().isoformat(),
        "run_type": run_type,
        "status": status,
        "details": details,
        "suburbs": suburbs or [],
    })
    # Keep last 200 entries
    _write_json(DATA_DIR / "agent_runs.json", runs[-200:])


# ---------------------------------------------------------
# DCP Harvest Tracking (run-once per council)
# ---------------------------------------------------------
def get_dcp_status() -> dict:
    """Return DCP harvest status: {council_name: {status, timestamp, docs}}."""
    return _read_json(DATA_DIR / "dcp_status.json") or {}


def save_dcp_status(council_name: str, status: str, docs_count: int = 0, details: str = ""):
    """Mark a council's DCP as harvested."""
    all_status = get_dcp_status()
    all_status[council_name] = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "docs_ingested": docs_count,
        "details": details[:500],
    }
    _write_json(DATA_DIR / "dcp_status.json", all_status)


def is_dcp_harvested(council_name: str) -> bool:
    """Check if a council's DCP has already been successfully harvested."""
    status = get_dcp_status().get(council_name, {})
    return status.get("status") == "completed"


# ---------------------------------------------------------
# Seed Data (fallback when no agent runs have occurred)
# ---------------------------------------------------------
def is_seeded() -> bool:
    return (DATA_DIR / "suburbs.json").exists() and len(get_suburbs()) > 0
