# MAS Sydney Residential Development Approvals

A multi-agent, MCP‑enabled system that scouts high‑ROI suburbs, audits properties, and generates council‑ready feasibility decks with GIS visuals, compliance risk, and executive reporting. This MAS is built for developers who want **fast, defensible feasibility signals** before formal DA submission.

## Why This Exists
This pipeline emulates a high‑performing property development team:
- Finds promising suburbs and properties.
- Performs geospatial due diligence.
- Ingests and queries council DCPs (RAG).
- Produces compliant concept proposals.
- Outputs a **premium PPTX slide deck** per property.

## What You Get
- End‑to‑end autonomous feasibility pipeline.
- GIS composite maps (hazards + zoning + hillshade) with legends.
- Listings and satellite imagery captured automatically.
- Compliance risk summaries and follow‑ups.
- A presentation‑ready slide deck for stakeholders.

---

## Architecture At A Glance

```mermaid
graph LR
  A[Socio‑Economic Analyst] --> B[Acquisition Scout]
  B --> C[Geospatial Surveyor]
  C --> D[Policy Archivist]
  D --> E[Compliance Officer]
  C --> F[Proposal Designer]
  F --> G[Compliance Checker]
  B --> H[Profile Merger]
  C --> H
  G --> I[Portfolio Builder]
  H --> I
  I --> J[Canva Slide Deck]
  I --> K[Executive Report]
```

---

## Core Workflow (Detailed)

```mermaid
graph TD
  S1[Socio‑Economic Scanner] --> S2[Property Scouting]
  S2 --> S3[Listing Image Capture]
  S2 --> S4[Site Survey + GIS]
  S4 --> S5[DCP Ingestion + RAG]
  S5 --> S6[Concept Proposal]
  S6 --> S7[Compliance Assessment]
  S3 --> S8[Profile Merge]
  S4 --> S8
  S7 --> S9[Portfolio Pack]
  S9 --> S10[Deck Manifest]
  S10 --> S11[Canva PPTX Deck]
```

---

## MCP Servers (2026 Choices)

| Server | Purpose | Transport | Env Required |
|---|---|---|---|
| `haris-musa/excel-mcp-server` | Direct Excel model updates | `uvx excel-mcp-server stdio` with SSE fallback | None |
| `Softeria/ms-365-mcp-server` | Full Microsoft Graph (Word, Outlook, OneDrive) | `npx @softeria/ms-365-mcp-server` | `CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID` |
| `@canva/cli@latest mcp` | Slide deck creation | `npx @canva/cli@latest mcp stdio` with SSE fallback | Canva auth |

---

## MCP Tools and Internal Tools

| Tool | Type | Purpose |
|---|---|---|
| `Property Scraper` | Browserbase + Playwright | Scrape Domain listings by suburb/postcode |
| `Listing Image Capturer` | Browserbase + Playwright | Capture full‑size listing photos |
| `Universal Browser` | Browserbase + Playwright | Generic deep page reader |
| `NSW Planning API` | HTTP | Zoning + council lookup via geocode |
| `Slope & Topography Analyzer` | Google Elevation API | Gradient + buildability verdict |
| `Hazard Overlay Checker` | NSW ArcGIS | Bushfire, flood, heritage overlays |
| `Satellite Vision Inspector` | Google Static Maps + Gemini VLM | Satellite image + VLM analysis |
| `Council DCP Crawler` | HTTP + Browserbase | Seeded DCP ingestion |
| `Autonomous DCP Harvester` | Browserbase search | DCP ingestion without seeds |
| `PDF Ingestion Engine` | Qdrant | DCP PDF ingestion into vector DB |
| `Qdrant Policy Query` | RAG | Retrieve DCP clauses for compliance |
| `Architecture Proposal Generator` | LLM | Concept proposal JSON |
| `Compliance Checker` | RAG + heuristics | Compliance summary and risk |
| `Portfolio Builder` | File outputs | Portfolio pack + deck manifest |
| `Council DA Tracker Scraper` | Browserbase + Playwright | DA tracker scraping with pagination |
| `GIS Composite Map` | Mapbox + ArcGIS | Hazards + zoning + hillshade visual |

---

## Agents And Responsibilities

| Agent | Role | Tools | MCP Connections |
|---|---|---|---|
| Socio‑Economic Analyst | Scores suburbs for ROI | `Socio‑Economic Suburb Scanner` | None |
| Acquisition Scout | Finds properties and images | `Property Scraper`, `Listing Image Capturer` | None |
| Geospatial Surveyor | Physical due diligence | `NSW Planning API`, `Slope`, `Hazard`, `Satellite` | None |
| Policy Archivist | Finds and ingests DCPs | `Autonomous DCP Harvester` | Qdrant |
| Compliance Officer | Retrieves DCP rules | `Qdrant Policy Query` | Qdrant |
| Proposal Designer | Concept proposal | `Architecture Proposal Generator` | None |
| Compliance Checker | Risk assessment | `Compliance Checker` | Qdrant |
| Profile Merger | Normalizes property JSON | `Property Profile Merger` | None |
| Portfolio Builder | Builds pack + deck | `Portfolio Builder`, Canva MCP | Canva MCP |
| Executive Assessor | Financial feasibility | Excel MCP tools | Excel MCP |
| Reporting Architect | Client deliverables | M365 MCP tools | Microsoft Graph MCP |

---

## RAG + Compliance Engine
This system ingests DCP PDFs into Qdrant, splits text into chunks, embeds with `all-MiniLM-L6-v2`, and queries for relevant clauses during compliance checks. Results are used to score risk and outline follow‑ups.

---

## GIS Composite Map Pipeline
The system creates a **single composite map image** for each property:
- Base: Mapbox style with hillshade.
- Overlays: ArcGIS hazard polygons + zoning polygons.
- Extras: Legend tile + elevation tag.

Outputs saved to `gis_maps/` and embedded in `deck_manifest.json`.

---

## Slide Deck Content (PPTX)
Each slide is built from the deck manifest and includes:
- Property summary (zoning, FSR, height, site area).
- Listing photos + satellite image.
- GIS composite map (hazards, zoning, hillshade).
- Architecture scheme table.
- Compliance outcome + follow‑up actions.

---

## Environment Variables

```ini
BROWSERBASE_API_KEY=
MAPBOX_API_KEY=
MAPBOX_STYLE=username/style_id
NSW_ZONING_ARCGIS_URL=https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/ePlanning/Planning_Portal_Principal_Planning/MapServer/27/query
GOOGLE_MAPS_API_KEY=
GEMINI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
```

---

## Key Output Paths

| Path | Description |
|---|---|
| `portfolio/<address>/portfolio.json` | Full data pack |
| `portfolio/<address>/portfolio.md` | Human readable summary |
| `portfolio/<address>/deck_manifest.json` | Slide deck blueprint |
| `gis_maps/composite_<lat>_<lng>.png` | Composite GIS map |
| `listing_images/<address>/` | Listing screenshots |
| `site_audits/satellite_<lat>_<lng>.png` | Satellite image |

---

## Notes For Production
- Keep ArcGIS as the authoritative data source.
- Use Mapbox only for rendering and presentation.
- For Canva automation, ensure CLI auth is valid.
- Add post‑processing to archive decks per council if needed.

---

## Roadmap Ideas
- Add a tileset pipeline for faster GIS rendering.
- Auto‑summarize DCP changes by council.
- Integrate Power Automate for client delivery.

---

## License
Internal use only.
