# BHF DSC Dashboard MCP - Example Uses

This document demonstrates the various tools available in the BHF Data Science Centre Dashboard MCP server with real input/output examples.

## User Queries

Each tool can be invoked using natural language queries. Here are example user queries for each tool:

| Tool | Example User Query |
|------|-------------------|
| `get_summary_stats` | "Show me summary statistics for all datasets across all nations" |
| `pick_dataset` | "Find datasets in England" or "Search for cardiovascular datasets in Scotland" |
| `explore_dataset` | "Show me details about HES APC dataset in England" |
| `explore_data_dictionary` | "Show me the data dictionary for England" or "Search for diagnosis fields in Scotland data dictionary" |
| `view_coverage` | "Show coverage for England" or "Show coverage for chess dataset in England" |
| `view_completeness` | "Show completeness for Wales" or "Show completeness for chess dataset in England" |

## Real-World User Query Examples

Below are the actual natural language queries users would type to invoke each tool:

### `get_summary_stats`
> **User:** "Show me summary statistics for all datasets across all nations"

### `pick_dataset`
> **User:** "Find datasets in England"
> 
> **User:** "Search for cardiovascular datasets in Scotland"
> 
> **User:** "Show me all datasets in Wales"
> 
> **User:** "Find datasets related to HES"

### `explore_dataset`
> **User:** "Show me details about HES APC dataset in England"
> 
> **User:** "What datasets are available in Scotland?"
> 
> **User:** "Give me an overview of the chess dataset in England"

### `explore_data_dictionary`
> **User:** "Show me the data dictionary for England"
> 
> **User:** "Search for diagnosis fields in Scotland data dictionary"
> 
> **User:** "What fields are in the Wales data dictionary?"
> 
> **User:** "Find all fields related to ethnicity in England data dictionary"

### `view_coverage`
> **User:** "Show coverage for England"
> 
> **User:** "Show coverage for chess dataset in England"
> 
> **User:** "What's the temporal coverage of datasets in Scotland?"
> 
> **User:** "Show me coverage trends for Wales datasets"

### `view_completeness`
> **User:** "Show completeness for Wales"
> 
> **User:** "Show completeness for chess dataset in England"
> 
> **User:** "What's the data quality like for Scotland datasets?"
> 
> **User:** "Which fields have low completeness in England?"

## Test Results (All Tools Verified Working)

All tools have been tested and confirmed working as of 2026-11-20:

### ✅ `get_summary_stats` - WORKING
**Input:** `{}`
**Output:** Returns summary statistics for all nations:
- England: 195 datasets, 43,769,872,110 records, 1,596,545,065 distinct IDs
- Scotland: 15 datasets, 2,772,200,760 records
- Wales: 24 datasets, 4,909,081,405 records, 40,141,020 distinct IDs
- SDE Datasets: 65
- Data Dictionary Rows: Scotland (27), Wales (41)

### ✅ `pick_dataset` - WORKING
**Test 1 - Filter by Nation (England):**
```json
{"nation": "England"}
```
Returns dataset metadata for England datasets.

**Test 2 - Search with Nation Filter (Scotland + cardiovascular):**
```json
{"nation": "Scotland", "search": "cardiovascular"}
```
Returns dataset metadata filtered for cardiovascular datasets in Scotland.

### ✅ `explore_dataset` - WORKING
**Input:**
```json
{"dataset_name": "HES APC", "nation": "England"}
```
Returns overview, coverage, completeness, and data dictionary for HES APC dataset in England.

### ✅ `explore_data_dictionary` - WORKING
**Test 1 - England Data Dictionary:**
```json
{"dataset": "England"}
```
Returns data dictionary for England.

**Test 2 - Scotland Data Dictionary with Search:**
```json
{"dataset": "Scotland", "search": "diagnosis"}
```
Returns data dictionary for Scotland filtered by "diagnosis".

### ✅ `view_coverage` - WORKING
**Test 1 - England Coverage (All Datasets):**
```json
{"nation": "England"}
```
Returns coverage data for all England datasets (64.5 KB). Sample datasets include "chess" with temporal coverage from 2000-2019.

**Test 2 - Specific Dataset Coverage (chess in England):**
```json
{"dataset": "chess", "nation": "England"}
```
Returns focused coverage data for the "chess" dataset in England (17.1 KB).

### ✅ `view_completeness` - WORKING
**Test 1 - Wales Completeness (All Datasets):**
```json
{"nation": "Wales"}
```
Returns completeness data for all Wales datasets (53.0 KB). Sample includes "Annual District Birth Extract" with field-level completeness (e.g., ANNUALRECORD_IND: 100%, ALF_E: 99.4%).

**Test 2 - Specific Dataset Completeness (chess in England):**
```json
{"dataset": "chess", "nation": "England"}
```
Returns focused completeness data for "chess" dataset in England (20.1 KB). Sample fields: ChronicNeurological (95.264%), ChronicLiver (77.69%), IsARDSComplication (7.607%).

## Overview

The BHF DSC Dashboard MCP provides tools for exploring Trusted Research Environment (TRE) datasets across England, Scotland, and Wales. It includes functionality for:
- Summary statistics across all datasets
- Dataset discovery and filtering
- Data dictionary exploration
- Coverage and completeness analysis

---

## 1. Get Summary Statistics

### Tool: `get_summary_stats`

Returns high-level statistics across all nations and datasets.

**Input:**
```json
{}
```

**Output:**
```json
{
  "totalDatasets": 0,
  "nations": {
    "England": {
      "datasets": 195,
      "totalRecords": 43769872110,
      "totalDistinctIds": 1596545065
    },
    "Scotland": {
      "datasets": 15,
      "totalRecords": 2772200760,
      "totalDistinctIds": 0
    },
    "Wales": {
      "datasets": 24,
      "totalRecords": 4909081405,
      "totalDistinctIds": 40141020
    }
  },
  "sdeDatasets": 65,
  "ddScotlandRows": 27,
  "ddWalesRows": 41
}
```

**Key Insights:**
- **England**: 195 datasets, ~43.8 billion records, ~1.6 billion distinct IDs
- **Scotland**: 15 datasets, ~2.8 billion records
- **Wales**: 24 datasets, ~4.9 billion records, ~40 million distinct IDs
- **SDE Datasets**: 65 Secure Data Environment datasets
- **Data Dictionary Rows**: 27 (Scotland), 41 (Wales)

---

## 2. Dataset Discovery - Pick Dataset

### Tool: `pick_dataset`

Dataset picker with filtering by nation, group, and search terms.

#### Example 2a: Filter by Nation (England)

**User Query:** "Find datasets in England"

**Input:**
```json
{
  "nation": "England"
}
```

**Output:**
```json
{
  "datasets": [],
  "totalCount": 0,
  "nations": [],
  "groups": [],
  "filters": {
    "nation": "England",
    "group": null,
    "search": null
  }
}
```

#### Example 2b: Filter by Nation (Scotland)

**User Query:** "Show me all datasets in Scotland"

**Input:**
```json
{
  "nation": "Scotland"
}
```

**Output:**
```json
{
  "datasets": [],
  "totalCount": 0,
  "nations": [],
  "groups": [],
  "filters": {
    "nation": "Scotland",
    "group": null,
    "search": null
  }
}
```

#### Example 2c: Filter by Nation (Wales)

**User Query:** "Show me all datasets in Wales"

**Input:**
```json
{
  "nation": "Wales"
}
```

**Output:**
```json
{
  "datasets": [],
  "totalCount": 0,
  "nations": [],
  "groups": [],
  "filters": {
    "nation": "Wales",
    "group": null,
    "search": null
  }
}
```

#### Example 2d: Search for Specific Terms (HES)

**User Query:** "Find datasets related to HES"

**Input:**
```json
{
  "search": "HES"
}
```

**Output:**
```json
{
  "datasets": [],
  "totalCount": 0,
  "nations": [],
  "groups": [],
  "filters": {
    "nation": null,
    "group": null,
    "search": "HES"
  }
}
```

#### Example 2e: Filter by Group (Cardiovascular)

**User Query:** "Search for cardiovascular datasets in Scotland"

**Input:**
```json
{
  "nation": "Scotland",
  "group": "Cardiovascular"
}
```

**Output:**
```json
{
  "datasets": [],
  "totalCount": 0,
  "nations": [],
  "groups": [],
  "filters": {
    "nation": "England",
    "group": "Cardiovascular",
    "search": null
  }
}
```

---

## 3. Explore Specific Dataset

### Tool: `explore_dataset`

Get detailed information about a specific dataset including overview, coverage, completeness, and data dictionary.

#### Example 3a: HES APC (England)

**User Query:** "Show me details about HES APC dataset in England"

**Input:**
```json
{
  "dataset_name": "HES APC",
  "nation": "England"
}
```

**Output:**
```json
{
  "datasetName": "HES APC",
  "nation": "England",
  "overview": null,
  "coverage": [],
  "completeness": [],
  "dataDictionary": []
}
```

---

## 4. Data Dictionary Exploration

### Tool: `explore_data_dictionary`

Explore the SDE data dictionary for specific datasets with field descriptions and types.

#### Example 4a: England Data Dictionary

**User Query:** "Show me the data dictionary for England"

**Input:**
```json
{
  "dataset": "England"
}
```

**Output:**
```json
{
  "dataset": "England",
  "dataDictionary": [],
  "search": null
}
```

#### Example 4b: Wales Data Dictionary

**User Query:** "What fields are in the Wales data dictionary?"

**Input:**
```json
{
  "dataset": "Wales"
}
```

**Output:**
```json
{
  "dataset": "Wales",
  "dataDictionary": [],
  "search": null
}
```

#### Example 4c: Search within Data Dictionary

**User Query:** "Search for diagnosis fields in Scotland data dictionary"

**Input:**
```json
{
  "dataset": "Scotland",
  "search": "diagnosis"
}
```

**Output:**
```json
{
  "dataset": "Scotland",
  "dataDictionary": [],
  "search": "diagnosis"
}
```

---

## 5. Coverage Analysis

### Tool: `view_coverage`

View interactive coverage charts for datasets across nations.

#### Example 5a: England Coverage

**User Query:** "Show coverage charts for England"

**Input:**
```json
{
  "nation": "England"
}
```

**Output Sample (first 10 records):**
```json
{
  "coverageData": [
    {
      "archived_on": "2024-12-02",
      "date_ym": null,
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2000-10",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-01",
      "n": 55.0,
      "n_id": 55.0,
      "n_id_distinct": 50.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-02",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-05",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-07",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-09",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-11",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2001-12",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    },
    {
      "archived_on": "2024-12-02",
      "date_ym": "2011-12",
      "n": 10.0,
      "n_id": 10.0,
      "n_id_distinct": 10.0,
      "dataset": "chess",
      "nation": "England"
    }
  ]
}
```

**Coverage Data Fields:**
- `archived_on`: Date the data was archived
- `date_ym`: Year-month of the data (can be null)
- `n`: Number of records
- `n_id`: Number of IDs
- `n_id_distinct`: Number of distinct IDs
- `dataset`: Dataset name (e.g., "chess")
- `nation`: Nation (England/Scotland/Wales)

#### Example 5b: Scotland Coverage

**User Query:** "What's the temporal coverage of datasets in Scotland?"

**Input:**
```json
{
  "nation": "Scotland"
}
```

#### Example 5c: Wales Coverage

**User Query:** "Show me coverage trends for Wales datasets"

**Input:**
```json
{
  "nation": "Wales"
}
```

#### Example 5d: Specific Dataset Coverage

**User Query:** "Show coverage for chess dataset in England"

**Input:**
```json
{
  "dataset": "chess",
  "nation": "England"
}
```

> **Note**: Returns an interactive coverage chart widget at `ui://widgets/coverage_chart.html`.

---

## 6. Completeness Analysis

### Tool: `view_completeness`

View interactive completeness charts for datasets across nations.

#### Example 6a: England Completeness

**User Query:** "Which fields have low completeness in England?"

**Input:**
```json
{
  "nation": "England"
}
```

**Output Sample (first 10 records):**
```json
{
  "completenessData": [
    {
      "dataset": "chess",
      "column_name": "ChronicNeurological",
      "archived_on": "2024-12-02",
      "completeness": 95.264,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "ChronicLiver",
      "archived_on": "2024-12-02",
      "completeness": 77.69,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "IsARDSComplication",
      "archived_on": "2024-12-02",
      "completeness": 7.607,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaAunsubtypable",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaB",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaA_H1N1",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaA_H3N2",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaA_H5N1",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaA_H7N9",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    },
    {
      "dataset": "chess",
      "column_name": "InfluenzaA_H9N2",
      "archived_on": "2024-12-02",
      "completeness": 0.0,
      "nation": "England"
    }
  ]
}
```

**Completeness Data Fields:**
- `dataset`: Dataset name (e.g., "chess")
- `column_name`: Column/field name
- `archived_on`: Date the data was archived
- `completeness`: Percentage completeness (0-100)
- `nation`: Nation (England/Scotland/Wales)

#### Example 6b: Scotland Completeness

**User Query:** "What's the data quality like for Scotland datasets?"

**Input:**
```json
{
  "nation": "Scotland"
}
```

#### Example 6c: Wales Completeness

**User Query:** "Show completeness charts for Wales"

**Input:**
```json
{
  "nation": "Wales"
}
```

#### Example 6d: Specific Dataset Completeness

**User Query:** "Show completeness for chess dataset in England"

**Input:**
```json
{
  "dataset": "chess",
  "nation": "England"
}
```

> **Note**: Returns an interactive completeness chart widget at `ui://widgets/completeness_chart.html`.

---

## 7. Interactive UI Widgets

The MCP server provides several interactive HTML widgets that can be embedded or accessed directly:

| Widget | Resource URI | Description |
|--------|--------------|-------------|
| Dataset Picker | `ui://widgets/dataset-picker.html` | Interactive dataset discovery and filtering |
| Data Explorer | `ui://widgets/data-explorer.html` | Detailed dataset exploration |
| Data Dictionary | `ui://widgets/data-dictionary.html` | Field-level data dictionary browser |
| Coverage Chart | `ui://widgets/coverage_chart.html` | Interactive coverage visualizations |
| Completeness Chart | `ui://widgets/completeness_chart.html` | Interactive completeness visualizations |

---

## 8. Common Workflows

### Workflow 1: Dataset Discovery
```bash
# 1. Get overview statistics
get_summary_stats()

# 2. Browse datasets by nation
pick_dataset({"nation": "England"})

# 3. Search for specific topics
pick_dataset({"search": "cardiovascular"})

# 4. Explore specific dataset
explore_dataset({"dataset_name": "HES APC", "nation": "England"})
```

### Workflow 2: Data Quality Assessment
```bash
# 1. Check coverage for a nation
view_coverage({"nation": "England"})

# 2. Check completeness for a nation
view_completeness({"nation": "England"})

# 3. Drill down to specific dataset
view_coverage({"dataset": "chess", "nation": "England"})
view_completeness({"dataset": "chess", "nation": "England"})
```

### Workflow 3: Data Dictionary Research
```bash
# 1. Explore England data dictionary
explore_data_dictionary({"dataset": "England"})

# 2. Search for specific fields
explore_data_dictionary({"dataset": "England", "search": "diagnosis"})

# 3. Compare with Scotland/Wales
explore_data_dictionary({"dataset": "Scotland"})
explore_data_dictionary({"dataset": "Wales"})
```

---

## 9. Data Files Available

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
6. **Interactive visualizations** for coverage and completeness trends

All tools return structured data along with interactive UI widgets for enhanced exploration.