# BHFDSC CVD-COVID TRE Dashboard MCP Server

An MCP (Model Context Protocol) server for exploring the BHFDSC CVD-COVID TRE Dashboard data. This server provides text-based tools for exploring datasets across England, Scotland, and Wales.

## Features

- **Dataset Picker** - Explore TRE datasets with filtering by nation, group, and search terms
- **Data Explorer** - Detailed exploration of specific datasets including overview, coverage, completeness, and data dictionary
- **Coverage Charts** - Data coverage across nations and datasets
- **Completeness Charts** - Data completeness across nations and datasets
- **Data Dictionary Explorer** - Explore SDE data dictionary with field descriptions, types, and search
- **Summary Statistics** - Overview statistics across all datasets and nations

## Data Sources

The server loads data from the [BHFDSC/cvd-covid-tre-dashboard](https://github.com/BHFDSC/cvd-covid-tre-dashboard) repository:

- **TRE Dataset Link** - Metadata for 117 datasets across England, Scotland, and Wales
- **England Data** - Overall, coverage, and completeness data (195 datasets)
- **Scotland Data** - Overview, coverage, and completeness data (15 datasets)
- **Wales (SAIL) Data** - Overview, coverage, and completeness data (24 datasets)
- **Data Dictionaries** - DD_Scotland.xlsx, DD_Wales.xlsx, and SDE Data Dictionary (65 datasets)

## Quick Start (VS Code)

The server is hosted at `https://bhfdscdashboardmcp.onrender.com/mcp` — no local installation is needed to use it.

### Add the Server to VS Code

1. Create or open `.vscode/mcp.json` in your workspace (or run **MCP: Add Server** from the Command Palette to add it to your user profile).
2. Add the following configuration:

```json
{
  "servers": {
    "bhfdscdashboardmcp": {
      "type": "http",
      "url": "https://bhfdscdashboardmcp.onrender.com/mcp",
      "tools": ["*"]
    }
  }
}
```

3. Save the file. VS Code will start the server and you can view its status and tools under the **MCP** section of the Extensions view (or via **MCP: List Servers** in the Command Palette).

### Use the Tools in Copilot Chat

1. Open Copilot Chat and switch to **Agent mode**.
2. Select the `bhfdscdashboardmcp` server's tools via the **Tools** icon in the chat input.
3. Ask questions in natural language, for example:

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

**Response**
Here are the details for the **Welsh Longitudinal General Practice (WLGP)** dataset in Wales (data archived 11/01/2024):

## Overview

| Metric | Value |
|---|---|
| Dataset | Welsh Longitudinal General Practice |
| Total records | **4,188,850,940** (~4.19 billion) |
| Records with ID | 4,183,859,725 (99.9%) |
| Distinct patients | **5,058,570** (~5.06 million) |

## Coverage

The coverage table shows the earliest date groups in the dataset. The bulk of the 4.19B records sit in recent years, but the returned rows highlight the historical tail:

| Date group | Records | Distinct patients |
|---|---|---|
| 101 (anomalous) | 2,057,630 | 712,005 |
| 1800-01 | 48,540 | 13,750 |
| 1800-02 → 1877-03 | ~10 each | ~10 each |

The pre-1900 entries (10–48K records each) are almost certainly data-quality anomalies or placeholder dates rather than genuine GP interactions — consistent with the dataset's stated start date of January 1950.

## Field Completeness (21 columns)

**Fully complete (100%):** ALF_STS_CD, GNDR_CD, WOB, PRAC_CD_E, LOCAL_NUM_E, EVENT_CD_VRS, EVENT_DT, EPISODE, SEQUENCE, DELTA_KEY, EVENT_YR, CREATE_DT, AVAIL_FROM_DT, SOURCE_EXTRACT

**Near-complete (99%+):** REG_CAT_CD (99.99999%), LSOA_CD (99.71%), EVENT_CD (99.28%)

**Low completeness:**
- EVENT_VAL — **48.55%** (the clinical value field is only populated for about half of events)
- ALF_MTCH_PCT — **0.29%**
- BATCH_NUM — **0.22%**

## Data Dictionary

The data dictionary for WLGP is currently **empty** in the dashboard export (no field definitions available).

**Key takeaway:** WLGP is a massive longitudinal dataset — 4.19 billion events across 5.06 million patients since 1950. Core identifiers, demographics, and event dates are essentially complete, but the clinical value field (EVENT_VAL) is only ~49% populated, which matters for analyses relying on test results or measurements.

### `explore_data_dictionary`
> **User:** "Using bhfdscdashboardMCP Show me the data dictionary for Scotland"

**Response**:
Here's the data dictionary situation for **Scotland** in the TRE dashboard:

## Data Dictionary Availability

The formal data dictionaries are **not available** for Scotland datasets in this dashboard export (archived 2023-08-11). The dashboard flags each dataset's dictionary status:

| Dataset | Dictionary available? | Reason |
|---|---|---|
| ECOSS | ⚠️ Flagged | "This dataset has been archived and we do not currently hold an archived data dictionary" |
| Vaccination | ⚠️ Flagged | "Data dictionary currently unavailable for this dataset" |
| SICSAG Daily / SICSAG Episodes | ⚠️ Flagged | "Data dictionary currently unavailable for this dataset" |
| Renal Registry | ⚠️ Flagged | "Data dictionary currently unavailable for this dataset" |
| All others (SMR00, SMR01, A&E, Deaths, PIS, SSCA, Diabetes, etc.) | ❌ No dictionary | — |

## Closest Alternative: Field-Level Completeness (column names per dataset)

While formal dictionaries are missing, the dashboard does export **column names with completeness** for 16 Scotland datasets — effectively a field list:

| Dataset | Columns | Example fields |
|---|---|---|
| **SMR01** (inpatient) | 56 | anon_id, sex, age, date_of_birth, admission_date, admission_type, location |
| **SMR00** (outpatient) | 55 | clinic_date, clinic_attendance, specialty, patient_category |
| **A&E** | 52 | arrival_date_time, discharge_date_time, attendance_category_code |
| **PIS dispensed** | 47 | prescribed_date, dispensed_date, paid_date, care_home_indicator |
| **PIS paid** | 45 | age_at_paid_date, paid_gic_excl_bb |
| **PIS prescribed** | 44 | prescription_line_no, age_at_prescribed_date, no_items |
| **SSCA** (stroke) | 38 | q3_admitting_hospital, q22_inpt_brain_imaging_done, q33a_pt_managed_in_asu |
| **Deaths** | 36 | marital_status, date_of_death, post_mortem_indicator |
| **Diabetes Covs** | 27 | diabetes_type, on_insulin, on_sglt2i, on_dpp4i |
| **ECOSS** | 29 | health_board, specimen_date, original_organism |
| **Covid Tests (L&ECOSS)** | 28 | test_result, test_type, ecoss_submitting_laboratory |
| **COG-UK** | 23 | lineage, pillar_2, sample_date, epi_week |
| **Vaccination** | 16 | vacc_dose_number, age_at_vacc, vacc_data_source |
| **SICSAG Episodes** | 15 | admitunit, admittime, disctime, destination, level |
| **SICSAG Daily** | 8 | haemofilt, inotrope, advanced_ventilation_derived |

**Key takeaway:** Formal data dictionaries aren't held for Scotland datasets in this dashboard — for full field definitions you'd need the [Public Health Scotland National Data Catalogue](https://publichealthscotland.scot/resources-and-tools/health-intelligence-and-data-management/national-data-catalogue/) or the HDR UK Gateway links per dataset. The completeness export does give you the complete column list per dataset, which I can show in full for any specific dataset if useful.

### `view_coverage`
> **User:** "Using bhfdscdashboardMCP Show total coverage for GDPPR in England"

**Response:**
Here's the total coverage for **GDPPR (GP Data – Planned Record)** in **England** (archived 2025-11-04):

## Overall Totals

| Metric | Value |
|---|---|
| **Total records** | **16,256,613,230** (~16.26 billion) |
| Records with ID | 16,256,613,230 (100%) |
| Max distinct patients in a single month | 33,890,110 (~33.9M — consistent with the England population) |
| Date groups | 1,841 monthly buckets |

## Coverage Range

- **Plausible range:** January 1900 → December 2030 (1,557 monthly groups holding 16.25B records)
- **Anomalous dates:** 283 groups (1760–1900 and 2031–2919) holding only ~77,525 records — clearly data-quality artifacts (placeholder/typo dates), not real GP records
- **Null date group:** 5,240,520 records with no date

## Records by Year (recent)

| Year | Records |
|---|---|
| 2021 | 2.04 billion |
| 2022 | 2.18 billion |
| 2023 | 2.26 billion |
| 2024 | 2.04 billion |
| 2025 | 1.40 billion (partial year at archive date) |
| 2026+ | negligible (anomalous future dates) |

## Peak Months

| Month | Records | Distinct patients |
|---|---|---|
| 2023-03 | 207.5M | 22.0M |
| 2023-10 | 206.8M | 23.8M |
| 2022-10 | 206.2M | 24.9M |
| 2022-11 | 202.5M | 23.7M |
| 2024-10 | 197.2M | 24.6M |

**Key takeaway:** GDPPR is the largest dataset in the England TRE at ~16.3 billion records, with monthly extracts covering ~22–25 million distinct patients per month. Coverage is effectively continuous from 1900 onward (with the bulk of data from 2021–2025), though a small number of records carry implausible dates that should be excluded in analysis.

### `view_completeness`
> **User:** "Using bhfdscdashboardMCP Show completeness for PEDW diagnosis table."

**Response**:
The **Patient Episode Database for Wales (PEDW)**. The diagnosis table is **"Patient Episode Datbase for Wales (Diagnostic codes)"** (archived 2024-01-11):

## PEDW — Diagnostic Codes Table Completeness (10 columns)

| Column | Completeness |
|---|---|
| PROV_UNIT_CD (provider unit) | 100.00% |
| EPI_NUM (episode number) | 100.00% |
| DIAG_NUM (diagnosis position) | 100.00% |
| DIAG_CD_123 (diagnosis code, 3-char) | 100.00% |
| DIAG_CD_1234 (diagnosis code, 4-char) | 100.00% |
| DIAG_CD (diagnosis code) | 100.00% |
| AVAIL_FROM_DT (availability date) | 100.00% |
| SPELL_NUM_E (spell number) | 100.00% |
| DIAG_CD_4 (4th diagnosis position) | 99.93% |
| **DIAG_CD_56 (5th–6th diagnosis positions)** | **6.09%** |

## For Context: PEDW Spells Table (main episode table, 50 columns)

Core fields are essentially complete: admission/discharge dates and methods, provider, specialty, spell/episode numbers, gender (99.70%), LSOA geography (98.6–99.3%), ethnicity code (88.24%).

Weaker fields: admission decision date (80.81%), HRG cost/code fields (51–56%), duration of elective wait (45.64%), and ALF_MTCH_PCT (1.09%).

**Key takeaway:** The PEDW diagnosis table is in excellent shape — primary diagnosis codes (positions 1–4) are ~100% populated. The only sparse field is DIAG_CD_56 (5th/6th diagnosis positions at 6.09%), which is expected since most episodes don't extend that far into secondary diagnoses.


## Data Files Available

The following data files are available in the `data/` directory:

| File | Description |
|------|-------------|
| `DD_England.xlsx` | SDE Data Dictionary |
| `DD_Scotland.xlsx` | Scotland Data Dictionary |
| `DD_Wales.xlsx` | Wales Data Dictionary |
| `export_dashboard_WALES_20240111_data_completeness.csv` | SAIL Completeness Data |
| `export_dashboard_WALES_20240111_data_coverage.csv` | SAIL Coverage Data |
| `export_dashboard_WALES_20240111_data_overview.csv` | SAIL Overview Data |
| `export_dashboard_england_20251104_data_completeness.csv` | England Completeness Data |
| `export_dashboard_england_20251104_data_coverage.csv` | England Coverage Data |
| `export_dashboard_england_20251104_data_overall.csv` | England Overall Data |
| `export_dashboard_scotland_completeness20230811.csv` | Scotland Completeness Data |
| `export_dashboard_scotland_coverage20230811.csv` | Scotland Coverage Data |
| `export_dashboard_scotland_overview20230811.csv` | Scotland Overview Data |

---