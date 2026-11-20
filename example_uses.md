# BHF DSC Dashboard MCP - Example Uses

This document demonstrates the various tools available in the BHF Data Science Centre Dashboard MCP server with real input/output examples.

## User Queries

Each tool can be invoked using natural language queries. Here are example user queries for each tool:

| Tool | Example User Query |
|------|-------------------|
| `get_summary_stats` | "Using bhfdscdashboardMCP Show me summary statistics for the HES APC dataset in England" |
| `pick_dataset` | "Using bhfdscdashboardMCP Find primary care dataset in Wales" |
| `explore_dataset` | "Using bhfdscdashboardMCP Show me details about WLGP dataset in Wales" |
| `explore_data_dictionary` | "Using bhfdscdashboardMCP Show me the data dictionary for Scotland" |
| `view_coverage` | "Using bhfdscdashboardMCP Show coverage for GDPPR in England" |
| `view_completeness` | "Using bhfdscdashboardMCP Show completeness for pedew diagnosis table" |

## Real-World User Query Examples

Below are the actual natural language queries users would type to invoke each tool:

### `get_summary_stats`
> **User:** "Using bhfdscdashboardMCP Show me summary statistics for the HES APC dataset in England" 

**Response:** 
Here's the summary for **HES APC (Admitted Patient Care)** in **England**, from the TRE dashboard data (archived 2025-11-04):

## Overview

| Metric | Value |
|---|---|
| Dataset | `hes_apc` |
| Nation | England |
| Total records | 509,647,645 |
| Records with ID | 509,647,645 (100%) |
| Distinct IDs | 77,570,205 |

## Coverage (earliest date groups returned)

The coverage table shows the earliest date groups in the dataset — the bulk of the 509M records sit in recent years, but the returned rows highlight the historical tail:

| Date | Records | Distinct IDs |
|---|---|---|
| *(missing date)* | 159,820 | 146,920 |
| 1800-01 | 1,820 | 1,760 |
| 1801-01 | 7,010 | 6,870 |
| 1924-05 → 1935-11 | ~10–20 per month | ~10 each |

These pre-1936 entries are tiny (10–20 records each) and likely represent data-quality anomalies or placeholder dates rather than genuine admissions.

## Field Completeness (50 columns)

**Fully complete (100%):** ProductionDate, EPIKEY, SEX, PROCODE5, ADMIMETH, WAITLIST, ETHNOS, EPITYPE

**High completeness (80–100%):** EPISTART (99.97%), MAINSPEF (99.97%), EPIDUR (99.83%), EPIEND (99.76%), STARTAGE_CALC (99.33%), ALCFRAC (87.78%), LSOA11 (82.76%), RESGOR (80.42%), PCTTREAT (80.42%)

**Moderate (50–80%):** ELECDATE (74.31%), CCG_RESIDENCE (63.19%), CCG_TREATMENT_ORIGIN (63.19%), RESCTY_ONS (59.52%), OPERTN_COUNT (59.08%), SPELDUR_CALC (50.05%)

**Low (<50%):** Diagnosis fields drop off quickly — DIAG_4_05 (35.28%), DIAG_3_07 (22.20%), DIAG_3_10 (11.43%) — and operation fields are sparse: OPERTN_3_08 (1.75%), OPERTN_4_17 (0.13%)

**Key takeaway:** Core episode and demographic fields are essentially complete, but secondary diagnosis and operation fields become progressively sparser the further out you go (e.g., 4th+ diagnosis codes are only ~35% populated), which matters for any analysis relying on comorbidity or procedure coding.


### `pick_dataset`
> **User:** "Using bhfdscdashboardMCP find primary care datasets in Wales"

**Response:** 
Here are the Wales datasets related to primary care found in the TRE dashboard:

## Core Primary Care Dataset

### Welsh Longitudinal General Practice (WLGP)
- **Group:** Primary | **Status:** ✅ Dataset available
- **Coverage from:** January 1950
- **Link:** https://healthdatagateway.org/en/dataset/355
- **Description:** Contains attendance and clinical information for all general practice interactions, including patient symptoms, investigations, diagnoses, prescribed medication, and referrals to tertiary care. Covers **83% of the population of Wales** and **80% of GP practices**.

## Related Datasets Capturing Primary Care Activity

| Dataset | Group | Status | From | Description |
|---|---|---|---|---|
| **Welsh Dispensing Dataset (WDDS)** | Prescribing/Dispensing | ✅ Available | 2000-01 | GP and non-medical prescriber prescriptions dispensed in the community — all medicines, dressings, and appliances ([link](https://healthdatagateway.org/en/dataset/285)) |
| **Outpatient Referral Dataset (OPRD)** | Secondary Care | ✅ Available | 2009-01 | Complete referral pathway from primary care (GP, dental, A&E, self-referrals) to secondary care ([link](https://healthdatagateway.org/en/dataset/308)) |
| **Referral to Treatment Times (RTTD)** | Other | ⏳ Requested | 2000-01 | Total wait time from GP referral to hospital treatment ([link](https://healthdatagateway.org/en/dataset/349)) |
| **Welsh Demographic Service Dataset (WDSD)** | Other | ⏳ Requested | 2000-01 | Register of all individuals registered with a Welsh GP, including anonymised address and practice history ([link](https://healthdatagateway.org/en/dataset/359)) |

**Key takeaway:** WLGP is the main primary care dataset in Wales, with exceptionally long coverage (since 1950). WDDS complements it for prescribing, while WDSD provides the GP registration denominator population.

### `explore_dataset`
> **User:** "Using bhfdscdashboardMCP Show me details about WLGP dataset in Wales"

### `explore_data_dictionary`
> **User:** "Using bhfdscdashboardMCP Show me the data dictionary for Scotland"

### `view_coverage`
> **User:** "Using bhfdscdashboardMCP Show coverage for GDPPR in England"

### `view_completeness`
> **User:** "Using bhfdscdashboardMCP Show completeness for pedew diagnosis table."

## Data Files Available

The following data files are available in the `data/` directory:

| File | Description |
|------|-------------|
| `20240624_SDE_DD_391419_j3w9t.xlsx` | SDE Data Dictionary |
| `DD_Scotland.xlsx` | Scotland Data Dictionary |
| `DD_Wales.xlsx` | Wales Data Dictionary |
| `export_dashboard_SAIL_20240111_data_completeness.csv` | SAIL Completeness Data |
| `export_dashboard_SAIL_20240111_data_coverage.csv` | SAIL Coverage Data |
| `export_dashboard_SAIL_20240111_data_overview.csv` | SAIL Overview Data |
| `export_dashboard_england_20251104_data_completeness.csv` | England Completeness Data |
| `export_dashboard_england_20251104_data_coverage.csv` | England Coverage Data |
| `export_dashboard_england_20251104_data_overall.csv` | England Overall Data |
| `export_dashboard_scotland_completeness20230811.csv` | Scotland Completeness Data |
| `export_dashboard_scotland_coverage20230811.csv` | Scotland Coverage Data |
| `export_dashboard_scotland_overview20230811.csv` | Scotland Overview Data |

---

## 10. Running the MCP Server

To start the MCP server:

```bash
python mcp_server.py
```

The server will be available for tool calls via the MCP protocol.

---

## Summary

The BHF DSC Dashboard MCP provides a comprehensive toolkit for exploring UK health data across Trusted Research Environments. Key capabilities include:

1. **High-level statistics** across England, Scotland, and Wales
2. **Interactive dataset discovery** with filtering and search
3. **Detailed dataset exploration** with overview, coverage, completeness, and data dictionary
4. **Data quality analysis** through coverage and completeness metrics
5. **Data dictionary browsing** with search functionality