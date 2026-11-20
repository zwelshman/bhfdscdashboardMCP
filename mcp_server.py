"""BHFDSC CVD-COVID TRE Dashboard MCP Server — Interactive data exploration for TRE datasets.

Deploy with:
    Build:  pip install -e .
    Start:  python mcp_server.py
    Health: GET /health
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import TextContent, EmbeddedResource
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Line buffering so logs print instantly in cloud control panels
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Widget HTML resources
WIDGETS_DIR = Path(__file__).parent / "widgets"
RESOURCE_MIME_TYPE = "text/html;profile=mcp-app"

def load_widget(name: str) -> str:
    """Load widget HTML and inline the ext-apps bundle."""
    widget_path = WIDGETS_DIR / name
    if not widget_path.exists():
        return f"<html><body>Widget not found: {name}</body></html>"
    return widget_path.read_text(encoding="utf-8")

# Pre-load widgets
WIDGET_HTML = {
    "dataset-picker.html": load_widget("dataset_picker.html"),
    "data-explorer.html": load_widget("data_explorer.html"),
    "coverage-chart.html": load_widget("coverage_chart.html"),
    "completeness-chart.html": load_widget("completeness_chart.html"),
    "data-dictionary.html": load_widget("data_dictionary.html"),
}

# Explicit transport security
mcp: FastMCP = FastMCP(
    "BHFDSC CVD-COVID TRE Dashboard",
    instructions=(
        "This server provides interactive tools to explore the BHFDSC CVD-COVID TRE Dashboard data. "
        "Available tools:\n"
        "- pick_dataset: Interactive picker for TRE datasets across England, Scotland, and Wales\n"
        "- explore_dataset: Detailed exploration of a specific dataset including coverage, completeness, and data dictionary\n"
        "- view_coverage: Interactive coverage charts for datasets\n"
        "- view_completeness: Interactive completeness charts for datasets\n"
        "- explore_data_dictionary: Explore SDE data dictionary for specific datasets\n"
        "- get_summary_stats: Get overview statistics across all datasets and nations"
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=(
            os.environ.get("MCP_ENABLE_DNS_REBINDING_PROTECTION", "true").lower()
            not in ("false", "0", "no", "off")
        ),
        allowed_hosts=[
            h.strip()
            for h in os.environ.get("MCP_ALLOWED_HOSTS", "localhost:*,127.0.0.1:*,localhost:8000,127.0.0.1:8000,bhfdscdashboardmcp.onrender.com").split(",")
            if h.strip()
        ],
        allowed_origins=[
            o.strip()
            for o in os.environ.get("MCP_ALLOWED_ORIGINS", "").split(",")
            if o.strip()
        ],
    ),
)

# Data cache directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Data cache
DATA_CACHE: dict[str, Any] = {
    "tre_dataset_link": None,
    "england_overall": None,
    "england_coverage": None,
    "england_completeness": None,
    "sail_overview": None,
    "sail_coverage": None,
    "sail_completeness": None,
    "scotland_overview": None,
    "scotland_coverage": None,
    "scotland_completeness": None,
    "dd_scotland": None,
    "dd_wales": None,
    "sde_data_dict": None,
}

BASE_URL = "https://raw.githubusercontent.com/BHFDSC/cvd-covid-tre-dashboard/main/Data/"

# Local cache file mapping
CACHE_FILES = {
    "tre_dataset_link": "tre_dataset_link.csv",
    "england_overall": "export_dashboard_england_20251104_data_overall.csv",
    "england_coverage": "export_dashboard_england_20251104_data_coverage.csv",
    "england_completeness": "export_dashboard_england_20251104_data_completeness.csv",
    "sail_overview": "export_dashboard_SAIL_20240111_data_overview.csv",
    "sail_coverage": "export_dashboard_SAIL_20240111_data_coverage.csv",
    "sail_completeness": "export_dashboard_SAIL_20240111_data_completeness.csv",
    "scotland_overview": "export_dashboard_scotland_overview20230811.csv",
    "scotland_coverage": "export_dashboard_scotland_coverage20230811.csv",
    "scotland_completeness": "export_dashboard_scotland_completeness20230811.csv",
    "dd_scotland": "DD_Scotland.xlsx",
    "dd_wales": "DD_Wales.xlsx",
    "sde_data_dict": "20240624_SDE_DD_391419_j3w9t.xlsx",
}


async def load_data() -> None:
    """Load all data from local cache or GitHub into cache."""
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        # Load CSV files
        csv_keys = [
            "tre_dataset_link", "england_overall", "england_coverage", "england_completeness",
            "sail_overview", "sail_coverage", "sail_completeness",
            "scotland_overview", "scotland_coverage", "scotland_completeness"
        ]
        
        for key in csv_keys:
            cache_file = DATA_DIR / CACHE_FILES[key]
            if cache_file.exists() and cache_file.stat().st_size > 100:
                print(f"Loading {key} from local cache...", file=sys.stderr)
                try:
                    DATA_CACHE[key] = pd.read_csv(cache_file).to_dict("records")
                except Exception as e:
                    print(f"Cache file corrupted, re-downloading {key}: {e}", file=sys.stderr)
                    cache_file.unlink(missing_ok=True)
            
            if key not in DATA_CACHE or DATA_CACHE[key] is None:
                print(f"Downloading {key} from GitHub...", file=sys.stderr)
                resp = await client.get(BASE_URL + CACHE_FILES[key])
                if resp.status_code == 200:
                    cache_file.write_bytes(resp.content)
                    DATA_CACHE[key] = pd.read_csv(pd.io.common.StringIO(resp.text)).to_dict("records")
                else:
                    print(f"Failed to download {key}: {resp.status_code}", file=sys.stderr)
                    DATA_CACHE[key] = []

        # Load Excel files
        excel_keys = ["dd_scotland", "dd_wales", "sde_data_dict"]
        
        for key in excel_keys:
            cache_file = DATA_DIR / CACHE_FILES[key]
            if cache_file.exists() and cache_file.stat().st_size > 100:
                print(f"Loading {key} from local cache...", file=sys.stderr)
                try:
                    if key == "sde_data_dict":
                        xls = pd.read_excel(cache_file, sheet_name=None)
                        DATA_CACHE[key] = {name: df.values.tolist() for name, df in xls.items()}
                    else:
                        df = pd.read_excel(cache_file, header=None)
                        DATA_CACHE[key] = df.values.tolist()
                except Exception as e:
                    print(f"Cache file corrupted, re-downloading {key}: {e}", file=sys.stderr)
                    cache_file.unlink(missing_ok=True)
            
            if key not in DATA_CACHE or DATA_CACHE[key] is None:
                print(f"Downloading {key} from GitHub...", file=sys.stderr)
                resp = await client.get(BASE_URL + CACHE_FILES[key])
                if resp.status_code == 200:
                    cache_file.write_bytes(resp.content)
                    if key == "sde_data_dict":
                        xls = pd.read_excel(pd.io.common.BytesIO(resp.content), sheet_name=None)
                        DATA_CACHE[key] = {name: df.values.tolist() for name, df in xls.items()}
                    else:
                        df = pd.read_excel(pd.io.common.BytesIO(resp.content), header=None)
                        DATA_CACHE[key] = df.values.tolist()
                else:
                    print(f"Failed to download {key}: {resp.status_code}", file=sys.stderr)
                    DATA_CACHE[key] = []

    print("All data loaded successfully", file=sys.stderr)


# Load data on import (will run when module is imported)
import asyncio
try:
    asyncio.run(load_data())
except RuntimeError:
    # If already in an event loop, schedule it
    pass


# Pydantic models for tool inputs
class PickDatasetInput(BaseModel):
    nation: str | None = Field(default=None, description="Filter by nation (England, Scotland, Wales, All)")
    group: str | None = Field(default=None, description="Filter by group (e.g., Primary, Secondary Care)")
    search: str | None = Field(default=None, description="Search term for dataset title/description")


class ExploreDatasetInput(BaseModel):
    dataset_name: str = Field(description="Name of the dataset to explore")
    nation: str = Field(description="Nation the dataset belongs to (England, Scotland, Wales)")


class ViewCoverageInput(BaseModel):
    nation: str | None = Field(default=None, description="Filter by nation (England, Scotland, Wales, All)")
    dataset: str | None = Field(default=None, description="Specific dataset to view")


class ViewCompletenessInput(BaseModel):
    nation: str | None = Field(default=None, description="Filter by nation (England, Scotland, Wales, All)")
    dataset: str | None = Field(default=None, description="Specific dataset to view")


class ExploreDataDictionaryInput(BaseModel):
    dataset: str = Field(description="Dataset name from SDE data dictionary")
    search: str | None = Field(default=None, description="Search term for field names/descriptions")


# Tool: Dataset Picker - Interactive picker for TRE datasets
@mcp.tool()
async def pick_dataset(
    nation: str | None = None,
    group: str | None = None,
    search: str | None = None,
) -> list[TextContent]:
    """Open an interactive picker to explore TRE datasets across England, Scotland, and Wales.
    
    Filter by nation, group, or search terms. Returns dataset metadata with interactive UI.
    """
    datasets = DATA_CACHE.get("tre_dataset_link", [])
    
    if nation and nation != "All":
        datasets = [d for d in datasets if d.get("Nation") == nation]
    if group:
        datasets = [d for d in datasets if d.get("Group") == group]
    if search:
        term = search.lower()
        datasets = [d for d in datasets if 
            term in str(d.get("Title", "")).lower() or
            term in str(d.get("Description", "")).lower() or
            term in str(d.get("Dataset", "")).lower()]
    
    nations = sorted(set(d.get("Nation") for d in datasets if d.get("Nation")))
    groups = sorted(set(d.get("Group") for d in datasets if d.get("Group")))
    
    result = {
        "datasets": datasets[:100],  # Limit for performance
        "totalCount": len(datasets),
        "nations": nations,
        "groups": groups,
        "filters": {"nation": nation, "group": group, "search": search},
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/dataset-picker.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Data Explorer - Explore dataset details
@mcp.tool()
async def explore_dataset(
    dataset_name: str,
    nation: str,
) -> list[TextContent]:
    """Explore detailed information about a specific dataset including coverage, completeness, and data dictionary."""
    
    # Select the right data based on nation
    if nation == "England":
        overview_data = DATA_CACHE.get("england_overall", [])
        coverage_data = DATA_CACHE.get("england_coverage", [])
        completeness_data = DATA_CACHE.get("england_completeness", [])
    elif nation == "Scotland":
        overview_data = DATA_CACHE.get("scotland_overview", [])
        coverage_data = DATA_CACHE.get("scotland_coverage", [])
        completeness_data = DATA_CACHE.get("scotland_completeness", [])
    elif nation == "Wales":
        overview_data = DATA_CACHE.get("sail_overview", [])
        coverage_data = DATA_CACHE.get("sail_coverage", [])
        completeness_data = DATA_CACHE.get("sail_completeness", [])
    else:
        overview_data = []
        coverage_data = []
        completeness_data = []
    
    # Find matching records
    overview = next((d for d in overview_data if d.get("dataset") == dataset_name or d.get("Dataset") == dataset_name), None)
    coverage = [d for d in coverage_data if d.get("dataset") == dataset_name or d.get("Dataset") == dataset_name]
    completeness = [d for d in completeness_data if d.get("dataset") == dataset_name or d.get("Dataset") == dataset_name]
    
    # Get data dictionary from SDE
    data_dict = DATA_CACHE.get("sde_data_dict", {}).get(dataset_name, [])
    
    result = {
        "datasetName": dataset_name,
        "nation": nation,
        "overview": overview,
        "coverage": coverage[:50],
        "completeness": completeness[:50],
        "dataDictionary": data_dict[:100],
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/data-explorer.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Coverage Chart - Visualize data coverage
@mcp.tool()
async def view_coverage(
    nation: str | None = None,
    dataset: str | None = None,
) -> list[TextContent]:
    """View interactive coverage charts for datasets across nations."""
    
    coverage_data = []
    
    if nation in ("England", "All", None):
        coverage_data.extend([{**d, "nation": "England"} for d in DATA_CACHE.get("england_coverage", [])])
    if nation in ("Scotland", "All", None):
        coverage_data.extend([{**d, "nation": "Scotland"} for d in DATA_CACHE.get("scotland_coverage", [])])
    if nation in ("Wales", "All", None):
        coverage_data.extend([{**d, "nation": "Wales"} for d in DATA_CACHE.get("sail_coverage", [])])
    
    if dataset:
        coverage_data = [d for d in coverage_data if d.get("dataset") == dataset or d.get("Dataset") == dataset]
    
    result = {
        "coverageData": coverage_data[:200],
        "nation": nation,
        "dataset": dataset,
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/coverage-chart.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Completeness Chart - Visualize data completeness
@mcp.tool()
async def view_completeness(
    nation: str | None = None,
    dataset: str | None = None,
) -> list[TextContent]:
    """View interactive completeness charts for datasets across nations."""
    
    completeness_data = []
    
    if nation in ("England", "All", None):
        completeness_data.extend([{**d, "nation": "England"} for d in DATA_CACHE.get("england_completeness", [])])
    if nation in ("Scotland", "All", None):
        completeness_data.extend([{**d, "nation": "Scotland"} for d in DATA_CACHE.get("scotland_completeness", [])])
    if nation in ("Wales", "All", None):
        completeness_data.extend([{**d, "nation": "Wales"} for d in DATA_CACHE.get("sail_completeness", [])])
    
    if dataset:
        completeness_data = [d for d in completeness_data if d.get("dataset") == dataset or d.get("Dataset") == dataset]
    
    result = {
        "completenessData": completeness_data[:200],
        "nation": nation,
        "dataset": dataset,
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/completeness-chart.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Data Dictionary Explorer - Explore SDE data dictionary
@mcp.tool()
async def explore_data_dictionary(
    dataset: str,
    search: str | None = None,
) -> list[TextContent]:
    """Explore the SDE data dictionary for specific datasets with field descriptions and types."""
    
    data_dict = DATA_CACHE.get("sde_data_dict", {}).get(dataset, [])
    
    if search:
        term = search.lower()
        filtered_dict = [row for row in data_dict if any(term in str(cell).lower() for cell in row)]
    else:
        filtered_dict = data_dict
    
    result = {
        "dataset": dataset,
        "dataDictionary": filtered_dict[:200],
        "search": search,
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/data-dictionary.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Summary Statistics - Get overview stats
@mcp.tool()
async def get_summary_stats() -> list[TextContent]:
    """Get summary statistics across all datasets and nations."""
    
    england_overall = DATA_CACHE.get("england_overall", [])
    scotland_overview = DATA_CACHE.get("scotland_overview", [])
    sail_overview = DATA_CACHE.get("sail_overview", [])
    
    def safe_sum(data, key):
        total = 0
        for d in data:
            val = d.get(key)
            if val is not None:
                try:
                    total += int(float(val))
                except (ValueError, TypeError):
                    pass
        return total
    
    stats = {
        "totalDatasets": len(DATA_CACHE.get("tre_dataset_link", [])),
        "nations": {
            "England": {
                "datasets": len(england_overall),
                "totalRecords": safe_sum(england_overall, "n"),
                "totalDistinctIds": safe_sum(england_overall, "n_id_distinct"),
            },
            "Scotland": {
                "datasets": len(scotland_overview),
                "totalRecords": safe_sum(scotland_overview, "n"),
                "totalDistinctIds": safe_sum(scotland_overview, "n_distinct"),
            },
            "Wales": {
                "datasets": len(sail_overview),
                "totalRecords": safe_sum(sail_overview, "n"),
                "totalDistinctIds": safe_sum(sail_overview, "n_distinct"),
            },
        },
        "sdeDatasets": len(DATA_CACHE.get("sde_data_dict", {})),
        "ddScotlandRows": len(DATA_CACHE.get("dd_scotland", [])),
        "ddWalesRows": len(DATA_CACHE.get("dd_wales", [])),
        "_meta": {
            "ui": {
                "resourceUri": "ui://widgets/data-explorer.html"
            }
        }
    }
    
    return [TextContent(type="text", text=str(stats))]


# Resource handlers for widgets
@mcp.resource("ui://widgets/dataset-picker.html", mime_type=RESOURCE_MIME_TYPE)
async def dataset_picker_widget() -> str:
    """Dataset picker widget."""
    return WIDGET_HTML["dataset-picker.html"]


@mcp.resource("ui://widgets/data-explorer.html", mime_type=RESOURCE_MIME_TYPE)
async def data_explorer_widget() -> str:
    """Data explorer widget."""
    return WIDGET_HTML["data-explorer.html"]


@mcp.resource("ui://widgets/coverage-chart.html", mime_type=RESOURCE_MIME_TYPE)
async def coverage_chart_widget() -> str:
    """Coverage chart widget."""
    return WIDGET_HTML["coverage-chart.html"]


@mcp.resource("ui://widgets/completeness-chart.html", mime_type=RESOURCE_MIME_TYPE)
async def completeness_chart_widget() -> str:
    """Completeness chart widget."""
    return WIDGET_HTML["completeness-chart.html"]


@mcp.resource("ui://widgets/data-dictionary.html", mime_type=RESOURCE_MIME_TYPE)
async def data_dictionary_widget() -> str:
    """Data dictionary widget."""
    return WIDGET_HTML["data-dictionary.html"]


# Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    """Health check endpoint for hosting platforms (Render)."""
    return JSONResponse({"status": "healthy", "mcp_endpoint": "/mcp"})


def main() -> None:
    """Serve the streamable-HTTP MCP transport at /mcp, binding env HOST/PORT."""
    mcp.settings.host = os.environ.get("HOST", "0.0.0.0")
    mcp.settings.port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()