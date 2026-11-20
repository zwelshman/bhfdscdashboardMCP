# BHF DSC Dashboard MCP - Example Uses

This document demonstrates the various tools available in the BHF Data Science Centre Dashboard MCP server with real input/output examples.

## User Queries

Each tool can be invoked using natural language queries. Here are example user queries for each tool:

| Tool | Example User Query |
|------|-------------------|
| `get_summary_stats` | "Using bhfdscdashboardMCP Show me summary statistics for all datasets across all nations" |
| `pick_dataset` | "Using bhfdscdashboardMCP Find datasets in England" |
| `explore_dataset` | "Using bhfdscdashboardMCP Show me details about HES APC dataset in England" |
| `explore_data_dictionary` | "Using bhfdscdashboardMCP Show me the data dictionary for England" |
| `view_coverage` | "Using bhfdscdashboardMCP Show coverage for England" |
| `view_completeness` | "Using bhfdscdashboardMCP Show completeness for Wales" |

## Real-World User Query Examples

Below are the actual natural language queries users would type to invoke each tool:

### `get_summary_stats`
> **User:** "Using bhfdscdashboardMCP Show me summary statistics for the HES APC dataset across in England" 

### `pick_dataset`
> **User:** "Using bhfdscdashboardMCP Find primary care dataset in Wales"

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