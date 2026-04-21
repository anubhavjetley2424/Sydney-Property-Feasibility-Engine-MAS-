# id.com.au Manual Download Guide

> **Frequency**: Once per quarter (data updates infrequently — Census every 5 years, forecasts annually, housing quarterly).
>
> **Time estimate**: ~30 minutes per council, ~2.5 hours total for all 5 councils.

## File Storage

Save all downloaded Excel files to:

```
backend/data/id_com/{council-slug}/{filename}.xlsx
```

Council slugs match your existing config:
| Council | Slug |
|---------|------|
| City of Parramatta | `parramatta` |
| The Hills Shire | `the-hills` |
| City of Ryde | `ryde` |
| Liverpool City | `liverpool` |
| Canterbury-Bankstown | `canterbury-bankstown` |

---

## Downloads Per Council

For each council, visit the pages below. On every page, click **Export → Excel** (top-right of the data table).

### 1. forecast.id.com.au — Population & Demand Signals

| Page | URL Pattern | Save As |
|------|------------|---------|
| Population & households & dwellings | `https://forecast.id.com.au/{slug}/population-households-dwellings` | `forecast_population_households.xlsx` |
| Residential development | `https://forecast.id.com.au/{slug}/residential-development` | `forecast_residential_development.xlsx` |
| Population summary | `https://forecast.id.com.au/{slug}/population-summary` | `forecast_population_summary.xlsx` |
| Components of change | `https://forecast.id.com.au/{slug}/components-of-population-change` | `forecast_components_change.xlsx` |

### 2. profile.id.com.au — Census Demographics

| Page | URL Pattern | Save As |
|------|------------|---------|
| Household income | `https://profile.id.com.au/{slug}/household-income` | `profile_household_income.xlsx` |
| Tenure overview | `https://profile.id.com.au/{slug}/tenure` | `profile_tenure.xlsx` |
| Dwelling type | `https://profile.id.com.au/{slug}/dwellings` | `profile_dwelling_type.xlsx` |
| Employment status | `https://profile.id.com.au/{slug}/employment-status` | `profile_employment.xlsx` |
| Population summary | `https://profile.id.com.au/{slug}/population` | `profile_population.xlsx` |
| Individual income | `https://profile.id.com.au/{slug}/individual-income` | `profile_individual_income.xlsx` |
| Housing rental payments | `https://profile.id.com.au/{slug}/housing-rental` | `profile_rental.xlsx` |
| Housing loan repayments | `https://profile.id.com.au/{slug}/housing-loan` | `profile_housing_loan.xlsx` |

### 3. housing.id.com.au — Market Signals

| Page | URL Pattern | Save As |
|------|------------|---------|
| Building approvals | `https://housing.id.com.au/{slug}/building-approvals` | `housing_building_approvals.xlsx` |
| Housing prices (if available) | `https://housing.id.com.au/{slug}/housing-prices` | `housing_prices.xlsx` |
| Rental overview | `https://housing.id.com.au/{slug}/rental-overview` | `housing_rental.xlsx` |
| Housing supply | `https://housing.id.com.au/{slug}/housing-supply` | `housing_supply.xlsx` |

> **Note**: housing.id.com.au may have slightly different page names per council. Download whatever data tables are available — the loader handles flexible filenames.

### 4. economy.id.com.au — Economic Engine

| Page | URL Pattern | Save As |
|------|------------|---------|
| Gross Regional Product | `https://economy.id.com.au/{slug}/gross-regional-product` | `economy_grp.xlsx` |
| Employment by industry | `https://economy.id.com.au/{slug}/employment-by-industry` | `economy_employment.xlsx` |
| Building approvals (value) | `https://economy.id.com.au/{slug}/building-approvals` | `economy_building_approvals.xlsx` |
| Local employment | `https://economy.id.com.au/{slug}/employment-total` | `economy_local_employment.xlsx` |
| Unemployment | `https://economy.id.com.au/{slug}/unemployment` | `economy_unemployment.xlsx` |

> **Note**: economy.id.com.au may require you to be logged in or may block automated access. If a page doesn't load, skip it — we have fallback data from ABS.

---

## Quick Start: Parramatta Example

```
backend/data/id_com/parramatta/
  forecast_population_households.xlsx
  forecast_residential_development.xlsx
  forecast_population_summary.xlsx
  forecast_components_change.xlsx
  profile_household_income.xlsx
  profile_tenure.xlsx
  profile_dwelling_type.xlsx
  profile_employment.xlsx
  profile_population.xlsx
  profile_rental.xlsx
  profile_housing_loan.xlsx
  housing_building_approvals.xlsx
  housing_prices.xlsx
  economy_grp.xlsx
  economy_employment.xlsx
  economy_building_approvals.xlsx
```

---

## After Downloading

Run the ingestion pipeline:
```bash
python -c "from backend.id_data_loader import load_all_councils; print(load_all_councils())"
```

Or trigger via the prospect workflow which now auto-loads local id.com data:
```bash
python run_id.py
```

The loader will:
1. Read all Excel files per council
2. Normalize into a standard schema
3. Merge into `suburbs.json` with enriched fields
4. Feed the prospect phase scoring

---

## Suburb-Level Data

Many id.com.au pages let you select **individual suburbs** via a dropdown before exporting.
For deeper suburb-level analysis, export the same page multiple times selecting different suburbs.

Save with a suffix: `forecast_population_households_blacktown.xlsx`, `forecast_population_households_seven_hills.xlsx`, etc.

The loader will auto-detect suburb-level files and aggregate them.
