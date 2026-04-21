"""
MAS Sydney – Excel Persistence Layer
======================================
Writes agent output data to Excel workbooks in parallel with JSON storage.
Uses the same _append_rows_to_excel helper pattern from tools.py.

Output files (in project root):
  prospectivity_trends.xlsx   – suburb scores, id metrics, DA trends, ranking
  council_da_tracker.xlsx     – DA records per council + combined sheet
  property_shortlist.xlsx     – scouted properties shortlist
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger("mas.excel_store")

_PROJECT_ROOT = Path(__file__).parent.parent
EXCEL_DIR = _PROJECT_ROOT  # Excel files live in project root


def _safe_path(filename: str) -> Path:
    return EXCEL_DIR / filename


def _append_rows_to_excel(path: Path, sheet: str, rows: list[dict]):
    """Append rows to an Excel sheet, creating the file if needed."""
    if not rows:
        return
    df_new = pd.DataFrame(rows)
    if path.exists():
        try:
            with pd.ExcelWriter(str(path), engine="openpyxl", mode="a",
                                if_sheet_exists="overlay") as writer:
                try:
                    df_existing = pd.read_excel(str(path), sheet_name=sheet)
                    df_out = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception:
                    df_out = df_new
                df_out.to_excel(writer, sheet_name=sheet, index=False)
        except Exception as e:
            logger.warning("Excel append failed for %s/%s, rewriting: %s", path, sheet, e)
            with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
                df_new.to_excel(writer, sheet_name=sheet, index=False)
    else:
        with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
            df_new.to_excel(writer, sheet_name=sheet, index=False)
    logger.info("Excel: wrote %d rows to %s / %s", len(rows), path.name, sheet)


def _write_full_sheet(path: Path, sheet: str, rows: list[dict]):
    """Overwrite a sheet entirely (no append)."""
    if not rows:
        return
    df = pd.DataFrame(rows)
    if path.exists():
        try:
            with pd.ExcelWriter(str(path), engine="openpyxl", mode="a",
                                if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)
        except Exception:
            with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet, index=False)
    else:
        with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet, index=False)


# ─────────────────────────────────────────────────
# Prospectivity Workbook (prospectivity_trends.xlsx)
# ─────────────────────────────────────────────────

def save_suburb_scores(suburbs: list[dict]):
    """Write suburb master data to Suburb_Scores sheet."""
    path = _safe_path("prospectivity_trends.xlsx")
    rows = []
    for s in suburbs:
        rows.append({
            "suburb": s.get("name", ""),
            "postcode": s.get("postcode", ""),
            "council": s.get("council", ""),
            "roi_score": s.get("roiScore"),
            "seifa_decile": s.get("seifaDecile"),
            "median_house_price": s.get("medianHousePrice"),
            "median_unit_price": s.get("medianUnitPrice"),
            "price_growth_5yr": s.get("priceGrowth5yr"),
            "rental_yield": s.get("rentalYield"),
            "pop_growth_5yr": s.get("popGrowth5yr"),
            "population": s.get("population"),
            "population_forecast_2036": s.get("populationForecast2036"),
            "building_approvals": s.get("buildingApprovals"),
            "median_income": s.get("medianIncome"),
            "unemployment": s.get("unemployment"),
            "immigration_rate": s.get("immigrationRate"),
            "emigration_rate": s.get("emigrationRate"),
            "net_migration": s.get("netMigration"),
            "verdict": s.get("verdict", ""),
            "updated_at": datetime.now().isoformat(),
        })
    _write_full_sheet(path, "Suburb_Scores", rows)

    # Build ranking sheet
    ranked = sorted(rows, key=lambda r: r.get("roi_score") or 0, reverse=True)
    for i, r in enumerate(ranked):
        r["rank"] = i + 1
    _write_full_sheet(path, "Ranking", ranked)


def save_id_metrics(suburb_id: str, suburb_name: str, metrics: dict):
    """Write id.com.au metrics to ID_Metrics sheet."""
    path = _safe_path("prospectivity_trends.xlsx")
    rows = []
    for source, data in metrics.items():
        if isinstance(data, dict):
            row = {"suburb": suburb_name, "source": source, "updated_at": datetime.now().isoformat()}
            row.update(data)
            rows.append(row)
    _append_rows_to_excel(path, "ID_Metrics", rows)


def save_da_trends_excel(suburb_id: str, suburb_name: str, trends: list[dict]):
    """Write DA monthly trends to DA_Trends sheet."""
    path = _safe_path("prospectivity_trends.xlsx")
    rows = [{"suburb": suburb_name, **t} for t in trends]
    _append_rows_to_excel(path, "DA_Trends", rows)


def save_population_excel(suburb_id: str, suburb_name: str, forecast: list[dict]):
    """Write population forecast to Population_Migration sheet."""
    path = _safe_path("prospectivity_trends.xlsx")
    rows = [{"suburb": suburb_name, **f} for f in forecast]
    _append_rows_to_excel(path, "Population_Migration", rows)


# ─────────────────────────────────────────────────
# Council DA Tracker Workbook (council_da_tracker.xlsx)
# ─────────────────────────────────────────────────

def save_da_records_excel(suburb_id: str, suburb_name: str, records: list[dict]):
    """Write DA records: one sheet per suburb + combined All_DAs sheet."""
    path = _safe_path("council_da_tracker.xlsx")
    stamped = [{"suburb": suburb_name, **r} for r in records]
    _write_full_sheet(path, suburb_name, stamped)
    _append_rows_to_excel(path, "All_DAs", stamped)


def save_hot_streets_excel(suburb_id: str, suburb_name: str, streets: list[dict]):
    """Write hot streets analysis to Hot_Streets sheet."""
    path = _safe_path("council_da_tracker.xlsx")
    rows = [{"suburb": suburb_name, **s} for s in streets]
    _append_rows_to_excel(path, "Hot_Streets", rows)


# ─────────────────────────────────────────────────
# Property Shortlist Workbook (property_shortlist.xlsx)
# ─────────────────────────────────────────────────

def save_properties_excel(suburb_id: str, suburb_name: str, properties: list[dict]):
    """Write scouted properties to the Shortlist sheet."""
    path = _safe_path("property_shortlist.xlsx")
    rows = []
    for p in properties:
        rows.append({
            "suburb": suburb_name,
            "address": p.get("address", ""),
            "price": p.get("price"),
            "land_size": p.get("landSize"),
            "bedrooms": p.get("bedrooms"),
            "bathrooms": p.get("bathrooms"),
            "zoning": p.get("zoning", ""),
            "fsr": p.get("fsr", ""),
            "max_height": p.get("maxHeight", ""),
            "roi_potential": p.get("roiPotential", ""),
            "listing_url": p.get("listingUrl", ""),
            "scouted_at": p.get("scoutedAt", datetime.now().isoformat()),
        })
    _append_rows_to_excel(path, "Shortlist", rows)


# ─────────────────────────────────────────────────
# DCP Summary Workbook (dcp_summary.xlsx)
# ─────────────────────────────────────────────────

def save_dcp_harvest_log(council_name: str, status: str, docs_count: int, details: str = ""):
    """Log a DCP harvest run."""
    path = _safe_path("dcp_summary.xlsx")
    _append_rows_to_excel(path, "Harvest_Log", [{
        "council": council_name,
        "status": status,
        "documents_ingested": docs_count,
        "details": details[:500],
        "timestamp": datetime.now().isoformat(),
    }])


# ─────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────

def get_excel_path(filename: str) -> Path | None:
    """Return path to an Excel file if it exists."""
    p = _safe_path(filename)
    return p if p.exists() else None
