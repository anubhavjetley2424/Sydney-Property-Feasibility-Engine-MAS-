"""
id.com.au Local Excel Ingestion Pipeline
==========================================
Reads manually-downloaded Excel files from backend/data/id_com/{council}/
and normalises them into a standard schema for the prospect phase.

Supports flexible filenames — matches on prefix keywords:
  forecast_population*, forecast_residential*, profile_household_income*,
  profile_tenure*, profile_dwelling*, housing_building*, economy_grp*, etc.

Each parser returns a flat dict of extracted metrics. The top-level
`load_council_id_data(slug)` merges them all into a single enrichment dict.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger("mas.id_loader")

_DATA_ROOT = Path(__file__).parent / "data" / "id_com"


# ------------------------------------------------------------------
# Utility helpers
# ------------------------------------------------------------------

def _find_file(council_dir: Path, *prefixes: str) -> Path | None:
    """Find the first Excel file matching any of the given prefixes."""
    if not council_dir.exists():
        return None
    for f in sorted(council_dir.iterdir()):
        if f.suffix.lower() in (".xlsx", ".xls", ".csv"):
            name_lower = f.stem.lower()
            for prefix in prefixes:
                if name_lower.startswith(prefix.lower()):
                    return f
    return None


def _read_excel_safe(path: Path, **kwargs) -> pd.DataFrame | None:
    """Read an Excel or CSV file, returning None on failure."""
    try:
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path, **kwargs)
        return pd.read_excel(path, **kwargs)
    except Exception as e:
        logger.warning("Failed to read %s: %s", path, e)
        return None


def _find_header_row(df: pd.DataFrame, keywords: list[str], max_rows: int = 15) -> int:
    """
    id.com.au Excel exports often have title/subtitle rows before the real header.
    Scan the first `max_rows` rows to find one containing any of the keywords.
    Returns the 0-based row index, or 0 if nothing is found.
    """
    for idx in range(min(max_rows, len(df))):
        row_text = " ".join(str(v).lower() for v in df.iloc[idx] if pd.notna(v))
        if any(kw.lower() in row_text for kw in keywords):
            return idx
    return 0


def _safe_int(val: Any) -> int | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        cleaned = str(val).replace(",", "").replace("$", "").replace("%", "").strip()
        if not cleaned or cleaned in (".", "-", ".."):
            return None
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None


def _safe_float(val: Any) -> float | None:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    try:
        cleaned = str(val).replace(",", "").replace("$", "").replace("%", "").strip()
        if not cleaned or cleaned in (".", "-", ".."):
            return None
        return round(float(cleaned), 2)
    except (ValueError, TypeError):
        return None


def _newest_year_col(df: pd.DataFrame) -> str | None:
    """Find the column with the most recent year number (e.g. 2026, 2031)."""
    year_cols = []
    for col in df.columns:
        m = re.search(r"(20\d{2})", str(col))
        if m:
            year_cols.append((int(m.group(1)), col))
    if year_cols:
        year_cols.sort(reverse=True)
        return year_cols[0][1]
    return None


def _col_containing(df: pd.DataFrame, *keywords: str) -> str | None:
    """Find the first column whose name contains any of the keywords."""
    for col in df.columns:
        col_lower = str(col).lower()
        for kw in keywords:
            if kw.lower() in col_lower:
                return col
    return None


# ------------------------------------------------------------------
# Domain-specific parsers
# ------------------------------------------------------------------

def _parse_forecast_population(path: Path) -> dict:
    """
    Parse forecast_population_households*.xlsx
    Expected columns include year-based headers with population, households, dwellings rows.
    """
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "population", "households", "dwellings", "2021", "2026"])
    if header_idx > 0:
        df = _read_excel_safe(path, header=header_idx)
    else:
        df = _read_excel_safe(path)

    if df is None or df.empty:
        return metrics

    # Try to extract population growth between first and last year columns
    year_cols = []
    for col in df.columns:
        m = re.search(r"(20\d{2})", str(col))
        if m:
            year_cols.append((int(m.group(1)), col))
    year_cols.sort()

    if len(year_cols) >= 2:
        first_year, first_col = year_cols[0]
        last_year, last_col = year_cols[-1]

        # Look for population row
        label_col = _col_containing(df, "area", "name", "category", "variable") or df.columns[0]
        for _, row in df.iterrows():
            label = str(row.get(label_col, "")).lower().strip()
            if "population" in label and "change" not in label and "rate" not in label:
                pop_start = _safe_int(row.get(first_col))
                pop_end = _safe_int(row.get(last_col))
                if pop_start and pop_end:
                    metrics["population_forecast_start"] = pop_start
                    metrics["population_forecast_start_year"] = first_year
                    metrics["population_forecast_end"] = pop_end
                    metrics["population_forecast_end_year"] = last_year
                    span = last_year - first_year
                    if span > 0 and pop_start > 0:
                        metrics["population_cagr_pct"] = round(
                            ((pop_end / pop_start) ** (1 / span) - 1) * 100, 2
                        )
                break

        # Households
        for _, row in df.iterrows():
            label = str(row.get(label_col, "")).lower().strip()
            if "household" in label and "size" not in label and "rate" not in label:
                hh_start = _safe_int(row.get(first_col))
                hh_end = _safe_int(row.get(last_col))
                if hh_start and hh_end:
                    metrics["households_forecast_start"] = hh_start
                    metrics["households_forecast_end"] = hh_end
                break

        # Dwellings
        for _, row in df.iterrows():
            label = str(row.get(label_col, "")).lower().strip()
            if "dwelling" in label and "size" not in label:
                dw_start = _safe_int(row.get(first_col))
                dw_end = _safe_int(row.get(last_col))
                if dw_start and dw_end:
                    metrics["dwellings_forecast_start"] = dw_start
                    metrics["dwellings_forecast_end"] = dw_end
                break

        # Average household size
        for _, row in df.iterrows():
            label = str(row.get(label_col, "")).lower().strip()
            if "average" in label and ("household" in label or "person" in label):
                size_end = _safe_float(row.get(last_col))
                if size_end:
                    metrics["avg_household_size_forecast"] = size_end
                break

    metrics["_source"] = str(path.name)
    return metrics


def _parse_forecast_residential_dev(path: Path) -> dict:
    """Parse forecast_residential_development*.xlsx — new dwelling pipeline."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "net", "dwelling", "new", "2021", "2026"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Sum net new dwellings across all year columns
    year_cols = [(int(re.search(r"(20\d{2})", str(c)).group(1)), c)
                 for c in df.columns if re.search(r"20\d{2}", str(c))]
    year_cols.sort()

    if year_cols:
        total_net_new = 0
        for _, col in year_cols:
            col_sum = df[col].apply(_safe_int).dropna().sum()
            total_net_new += col_sum
        if total_net_new > 0:
            metrics["total_net_new_dwellings_forecast"] = int(total_net_new)
            metrics["residential_dev_years"] = f"{year_cols[0][0]}-{year_cols[-1][0]}"

    metrics["_source"] = str(path.name)
    return metrics


def _parse_profile_income(path: Path) -> dict:
    """Parse profile_household_income*.xlsx or profile_individual_income*.xlsx."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["income", "number", "percent", "%", "total"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Try to find a median income value in the data
    full_text = df.to_string().lower()
    median_match = re.search(r"median[^$\d]*\$?([\d,]+)", full_text)
    if median_match:
        metrics["median_income_census"] = _safe_int(median_match.group(1))

    # Try to find high-income percentage ($2,000+/week or $104,000+/year)
    for _, row in df.iterrows():
        label = str(row.iloc[0]).lower() if len(row) > 0 else ""
        if any(k in label for k in ["2,000", "2000", "3,000", "3000", "high", "104,000"]):
            pct_col = _col_containing(df, "%", "percent")
            if pct_col:
                metrics["high_income_pct"] = _safe_float(row.get(pct_col))
            break

    metrics["_source"] = str(path.name)
    return metrics


def _parse_profile_tenure(path: Path) -> dict:
    """Parse profile_tenure*.xlsx — owner vs renter breakdown."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["tenure", "number", "percent", "%", "total", "owned", "rented"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    pct_col = _col_containing(df, "%", "percent")
    label_col = df.columns[0]

    for _, row in df.iterrows():
        label = str(row.get(label_col, "")).lower()
        pct_val = _safe_float(row.get(pct_col)) if pct_col else None
        if "rent" in label and "mortgage" not in label:
            if pct_val:
                metrics["renter_pct"] = pct_val
        elif ("owned" in label and "mortgage" in label) or "mortgage" in label:
            if pct_val:
                metrics["mortgage_pct"] = pct_val
        elif "owned outright" in label:
            if pct_val:
                metrics["owned_outright_pct"] = pct_val

    metrics["_source"] = str(path.name)
    return metrics


def _parse_profile_dwelling_type(path: Path) -> dict:
    """Parse profile_dwelling_type*.xlsx — detached vs medium/high density."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["dwelling", "number", "percent", "%", "type", "separate", "flat"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    pct_col = _col_containing(df, "%", "percent")
    label_col = df.columns[0]

    for _, row in df.iterrows():
        label = str(row.get(label_col, "")).lower()
        pct_val = _safe_float(row.get(pct_col)) if pct_col else None
        if "separate house" in label or "detached" in label:
            if pct_val:
                metrics["detached_house_pct"] = pct_val
        elif "flat" in label or "apartment" in label:
            if pct_val:
                metrics["apartment_pct"] = pct_val
        elif "semi" in label or "terrace" in label or "townhouse" in label or "medium density" in label:
            if pct_val:
                metrics["medium_density_pct"] = pct_val

    metrics["_source"] = str(path.name)
    return metrics


def _parse_profile_employment(path: Path) -> dict:
    """Parse profile_employment*.xlsx."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["employment", "number", "percent", "%", "labour", "unemploy"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    pct_col = _col_containing(df, "%", "percent")
    label_col = df.columns[0]

    for _, row in df.iterrows():
        label = str(row.get(label_col, "")).lower()
        pct_val = _safe_float(row.get(pct_col)) if pct_col else None
        if "unemploy" in label:
            if pct_val:
                metrics["unemployment_pct_census"] = pct_val
        elif "employed" in label and "part" not in label and "un" not in label:
            if pct_val:
                metrics["employed_full_time_pct"] = pct_val

    metrics["_source"] = str(path.name)
    return metrics


def _parse_housing_building_approvals(path: Path) -> dict:
    """Parse housing_building_approvals*.xlsx."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "approval", "number", "total", "dwelling"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Try to find the most recent year's total
    num_cols = [c for c in df.columns if df[c].apply(lambda x: _safe_int(x) is not None).any()]
    if num_cols:
        last_col = num_cols[-1]
        total = df[last_col].apply(_safe_int).dropna().sum()
        if total > 0:
            metrics["building_approvals_latest"] = int(total)

    metrics["_source"] = str(path.name)
    return metrics


def _parse_housing_prices(path: Path) -> dict:
    """Parse housing_prices*.xlsx — median sale prices."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "median", "price", "sale", "house", "unit"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Look for house and unit median prices
    full_text = df.to_string().lower()
    house_match = re.search(r"house[^$\d]*\$?([\d,]+)", full_text)
    unit_match = re.search(r"unit[^$\d]*\$?([\d,]+)", full_text)
    if house_match:
        metrics["median_house_price_id"] = _safe_int(house_match.group(1))
    if unit_match:
        metrics["median_unit_price_id"] = _safe_int(unit_match.group(1))

    metrics["_source"] = str(path.name)
    return metrics


def _parse_economy_grp(path: Path) -> dict:
    """Parse economy_grp*.xlsx — Gross Regional Product."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "gross", "product", "grp", "million", "billion"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Try to find the most recent GRP value
    full_text = df.to_string()
    grp_matches = re.findall(r"\$?([\d,.]+)\s*(?:billion|million|[bm])", full_text, re.IGNORECASE)
    if grp_matches:
        val = grp_matches[-1].replace(",", "")
        try:
            fval = float(val)
            # Heuristic: values < 100 are likely in billions
            if fval < 100:
                metrics["grp_billions"] = round(fval, 2)
            else:
                metrics["grp_millions"] = round(fval, 2)
        except ValueError:
            pass

    metrics["_source"] = str(path.name)
    return metrics


def _parse_economy_employment(path: Path) -> dict:
    """Parse economy_employment*.xlsx or economy_local_employment*.xlsx."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["year", "employment", "number", "industry", "total", "job"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Try to find total employment count
    full_text = df.to_string().lower()
    total_match = re.search(r"total[^0-9]*([\d,]+)", full_text)
    if total_match:
        metrics["local_jobs_total"] = _safe_int(total_match.group(1))

    metrics["_source"] = str(path.name)
    return metrics


def _parse_profile_rental(path: Path) -> dict:
    """Parse profile_rental*.xlsx — rental payment distribution."""
    metrics = {}
    raw = _read_excel_safe(path, header=None)
    if raw is None or raw.empty:
        return metrics

    header_idx = _find_header_row(raw, ["rental", "rent", "payment", "number", "percent", "%", "weekly"])
    df = _read_excel_safe(path, header=header_idx) if header_idx > 0 else _read_excel_safe(path)
    if df is None or df.empty:
        return metrics

    # Try to find median weekly rent
    full_text = df.to_string().lower()
    median_match = re.search(r"median[^$\d]*\$?([\d,]+)", full_text)
    if median_match:
        metrics["median_weekly_rent_census"] = _safe_int(median_match.group(1))

    metrics["_source"] = str(path.name)
    return metrics


# ------------------------------------------------------------------
# File → parser mapping
# ------------------------------------------------------------------

_PARSER_MAP = [
    # (file prefixes to match, parser function)
    (["forecast_population_household", "forecast_pop_hh"], _parse_forecast_population),
    (["forecast_residential", "forecast_res_dev"], _parse_forecast_residential_dev),
    (["forecast_population_summary", "forecast_pop_summary"], _parse_forecast_population),
    (["forecast_component", "forecast_comp"], _parse_forecast_population),
    (["profile_household_income", "profile_hh_income"], _parse_profile_income),
    (["profile_individual_income", "profile_ind_income"], _parse_profile_income),
    (["profile_tenure"], _parse_profile_tenure),
    (["profile_dwelling", "profile_dwell"], _parse_profile_dwelling_type),
    (["profile_employment", "profile_employ"], _parse_profile_employment),
    (["profile_rental", "profile_rent"], _parse_profile_rental),
    (["profile_housing_loan", "profile_loan"], _parse_profile_rental),
    (["housing_building_approval", "housing_approvals"], _parse_housing_building_approvals),
    (["housing_price", "housing_median"], _parse_housing_prices),
    (["housing_rental", "housing_rent"], _parse_profile_rental),
    (["housing_supply"], _parse_housing_building_approvals),
    (["economy_grp", "economy_gross"], _parse_economy_grp),
    (["economy_employment", "economy_employ", "economy_local"], _parse_economy_employment),
    (["economy_building", "economy_approval"], _parse_housing_building_approvals),
    (["economy_unemploy"], _parse_profile_employment),
]


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def load_council_id_data(slug: str) -> dict:
    """
    Load and merge all id.com.au Excel data for a single council.

    Args:
        slug: Council slug matching folder name, e.g. 'parramatta'

    Returns:
        Merged dict of all extracted metrics. Keys prefixed by domain.
        Returns empty dict if no data folder exists.
    """
    council_dir = _DATA_ROOT / slug
    if not council_dir.exists():
        logger.info("No id.com data folder for %s at %s", slug, council_dir)
        return {}

    merged = {}
    files_found = 0
    files_parsed = 0

    for f in sorted(council_dir.iterdir()):
        if f.suffix.lower() not in (".xlsx", ".xls", ".csv"):
            continue
        files_found += 1
        name_lower = f.stem.lower()

        # Find matching parser
        parsed = False
        for prefixes, parser_fn in _PARSER_MAP:
            if any(name_lower.startswith(p.lower()) for p in prefixes):
                try:
                    result = parser_fn(f)
                    if result:
                        # Merge without overwriting existing non-None values
                        for k, v in result.items():
                            if k == "_source":
                                continue
                            if v is not None and (k not in merged or merged[k] is None):
                                merged[k] = v
                        files_parsed += 1
                        parsed = True
                except Exception as e:
                    logger.warning("Parser failed for %s: %s", f.name, e)
                break

        if not parsed:
            logger.debug("No parser matched file: %s", f.name)

    merged["_files_found"] = files_found
    merged["_files_parsed"] = files_parsed
    logger.info("id.com loader: %s → %d files found, %d parsed, %d metrics",
                slug, files_found, files_parsed, len([k for k in merged if not k.startswith("_")]))
    return merged


def load_all_councils() -> dict[str, dict]:
    """
    Load id.com.au data for all councils that have data folders.

    Returns:
        Dict mapping council slug → metrics dict.
    """
    if not _DATA_ROOT.exists():
        logger.warning("id.com data root missing: %s. Creating it.", _DATA_ROOT)
        _DATA_ROOT.mkdir(parents=True, exist_ok=True)
        return {}

    results = {}
    for d in sorted(_DATA_ROOT.iterdir()):
        if d.is_dir():
            results[d.name] = load_council_id_data(d.name)
    return results


def enrich_suburb_record(suburb: dict, id_data: dict) -> dict:
    """
    Merge id.com.au metrics into an existing suburb record from suburbs.json.
    Only overwrites fields that are currently None/missing.

    Args:
        suburb: Existing suburb dict from data_store
        id_data: Output of load_council_id_data()

    Returns:
        Updated suburb dict (mutated in place and returned).
    """
    if not id_data:
        return suburb

    # Population forecast
    if id_data.get("population_forecast_end"):
        suburb.setdefault("populationForecast", id_data["population_forecast_end"])
        suburb.setdefault("populationForecastYear", id_data.get("population_forecast_end_year"))
    if id_data.get("population_cagr_pct"):
        if suburb.get("popGrowth5yr") is None:
            suburb["popGrowthCAGR"] = id_data["population_cagr_pct"]

    # Household / dwelling forecasts
    if id_data.get("households_forecast_end"):
        suburb.setdefault("householdsForecast", id_data["households_forecast_end"])
    if id_data.get("dwellings_forecast_end"):
        suburb.setdefault("dwellingsForecast", id_data["dwellings_forecast_end"])
    if id_data.get("avg_household_size_forecast"):
        suburb.setdefault("avgHouseholdSize", id_data["avg_household_size_forecast"])

    # Residential dev pipeline
    if id_data.get("total_net_new_dwellings_forecast"):
        suburb.setdefault("netNewDwellingsPipeline", id_data["total_net_new_dwellings_forecast"])

    # Income
    if id_data.get("median_income_census") and suburb.get("medianIncome") is None:
        suburb["medianIncome"] = id_data["median_income_census"]
    if id_data.get("high_income_pct"):
        suburb.setdefault("highIncomePct", id_data["high_income_pct"])

    # Housing tenure
    if id_data.get("renter_pct"):
        suburb.setdefault("renterPct", id_data["renter_pct"])
    if id_data.get("mortgage_pct"):
        suburb.setdefault("mortgagePct", id_data["mortgage_pct"])
    if id_data.get("owned_outright_pct"):
        suburb.setdefault("ownedOutrightPct", id_data["owned_outright_pct"])

    # Dwelling types
    if id_data.get("detached_house_pct"):
        suburb.setdefault("detachedHousePct", id_data["detached_house_pct"])
    if id_data.get("apartment_pct"):
        suburb.setdefault("apartmentPct", id_data["apartment_pct"])
    if id_data.get("medium_density_pct"):
        suburb.setdefault("mediumDensityPct", id_data["medium_density_pct"])

    # Employment
    if id_data.get("unemployment_pct_census") and suburb.get("unemployment") is None:
        suburb["unemployment"] = id_data["unemployment_pct_census"]
    if id_data.get("employed_full_time_pct"):
        suburb.setdefault("employedFullTimePct", id_data["employed_full_time_pct"])

    # Building approvals
    if id_data.get("building_approvals_latest"):
        if suburb.get("buildingApprovals") is None:
            suburb["buildingApprovals"] = id_data["building_approvals_latest"]

    # Housing prices from id.com
    if id_data.get("median_house_price_id"):
        suburb.setdefault("medianHousePriceId", id_data["median_house_price_id"])
    if id_data.get("median_unit_price_id"):
        suburb.setdefault("medianUnitPriceId", id_data["median_unit_price_id"])

    # Rental
    if id_data.get("median_weekly_rent_census"):
        suburb.setdefault("medianWeeklyRent", id_data["median_weekly_rent_census"])

    # Economy
    if id_data.get("grp_billions"):
        suburb.setdefault("grossRegionalProduct", f"${id_data['grp_billions']}B")
    elif id_data.get("grp_millions"):
        suburb.setdefault("grossRegionalProduct", f"${id_data['grp_millions']}M")
    if id_data.get("local_jobs_total"):
        if suburb.get("localEmployment") is None:
            suburb["localEmployment"] = id_data["local_jobs_total"]

    # Mark enrichment timestamp
    from datetime import datetime
    suburb["idComDataLoaded"] = datetime.now().isoformat()

    return suburb
