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
from mcp.types import TextContent
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Line buffering so logs print instantly in cloud control panels
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)


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

# Dataset name resolver - maps user-friendly names to dataset identifiers
DATASET_NAME_MAP: dict[str, str] = {}

BASE_URL = "https://raw.githubusercontent.com/BHFDSC/cvd-covid-tre-dashboard/main/Data/"

# Local cache file mapping
CACHE_FILES = {
    "tre_dataset_link": "TRE_dataset_link.csv",
    "england_overall": "export_dashboard_england_20251104_data_overall.csv",
    "england_coverage": "export_dashboard_england_20251104_data_coverage.csv",
    "england_completeness": "export_dashboard_england_20251104_data_completeness.csv",
    "sail_overview": "export_dashboard_WALES_20240111_data_overview.csv",
    "sail_coverage": "export_dashboard_WALES_20240111_data_coverage.csv",
    "sail_completeness": "export_dashboard_WALES_20240111_data_completeness.csv",
    "scotland_overview": "export_dashboard_scotland_overview20230811.csv",
    "scotland_coverage": "export_dashboard_scotland_coverage20230811.csv",
    "scotland_completeness": "export_dashboard_scotland_completeness20230811.csv",
    "dd_scotland": "DD_Scotland.xlsx",
    "dd_wales": "DD_Wales.xlsx",
    "sde_data_dict": "DD_England.xlsx",
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
                    # Ensure sde_data_dict is always a dict
                    if key == "sde_data_dict":
                        DATA_CACHE[key] = {}
                    else:
                        DATA_CACHE[key] = []

    print("All data loaded successfully", file=sys.stderr)
    
    # Build dataset name map for semantic matching
    build_dataset_name_map()


def build_dataset_name_map() -> None:
    """Build a mapping from user-friendly names to dataset identifiers."""
    global DATASET_NAME_MAP
    datasets = DATA_CACHE.get("tre_dataset_link", [])
    
    for d in datasets:
        dataset_id = d.get("Dataset", "")
        if not dataset_id or not isinstance(dataset_id, str):
            continue
        dataset_id = dataset_id.strip()
        if not dataset_id:
            continue
            
        # Map various name fields to the dataset identifier
        name_fields = [
            d.get("Title", ""),
            d.get("Shortname", ""),
            d.get("title_dataset", ""),
            d.get("dataset_dataset", ""),
            d.get("table", ""),
        ]
        
        for name in name_fields:
            if name and isinstance(name, str):
                clean_name = name.strip()
                if clean_name:
                    # Store lowercase for case-insensitive matching
                    DATASET_NAME_MAP[clean_name.lower()] = dataset_id
                    # Also store with common variations
                    DATASET_NAME_MAP[clean_name.lower().replace(" ", "_")] = dataset_id
                    DATASET_NAME_MAP[clean_name.lower().replace("-", "_")] = dataset_id
                    DATASET_NAME_MAP[clean_name.lower().replace("(", "").replace(")", "")] = dataset_id


def resolve_dataset_name(user_input: str, nation: str | None = None) -> str | None:
    """Resolve a user-friendly dataset name to the actual dataset identifier.
    
    Args:
        user_input: User's dataset name (e.g., "HES APC", "Hospital Episode Statistics")
        nation: Optional nation filter (England, Scotland, Wales)
    
    Returns:
        The dataset identifier (e.g., "hes_apc") or None if not found
    """
    if not user_input:
        return None
    
    # Direct match in map (case-insensitive)
    key = user_input.strip().lower()
    if key in DATASET_NAME_MAP:
        return DATASET_NAME_MAP[key]
    
    # Try with common variations
    variations = [
        key.replace(" ", "_"),
        key.replace("-", "_"),
        key.replace("(", "").replace(")", ""),
        key.replace(".", ""),
    ]
    
    for var in variations:
        if var in DATASET_NAME_MAP:
            return DATASET_NAME_MAP[var]
    
    # Fuzzy match: check if user input is contained in any known name
    datasets = DATA_CACHE.get("tre_dataset_link", [])
    user_lower = user_input.lower()
    
    for d in datasets:
        dataset_id = d.get("Dataset", "")
        if not dataset_id or not isinstance(dataset_id, str):
            continue
        dataset_id = dataset_id.strip()
        if not dataset_id:
            continue
            
        # Filter by nation if provided
        if nation and d.get("Nation") != nation:
            continue
        
        # Check all name fields
        name_fields = [
            d.get("Title", ""),
            d.get("Shortname", ""),
            d.get("title_dataset", ""),
            d.get("dataset_dataset", ""),
            d.get("table", ""),
        ]
        
        for name in name_fields:
            if name and isinstance(name, str):
                name_lower = name.lower()
                # Check if user input is a substring of the known name
                if user_lower in name_lower or name_lower in user_lower:
                    return dataset_id
    
    return None


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
    The search parameter supports semantic matching against Title, Shortname, Description, and Dataset identifier.
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
            term in str(d.get("Shortname", "")).lower() or
            term in str(d.get("Description", "")).lower() or
            term in str(d.get("Dataset", "")).lower() or
            term in str(d.get("title_dataset", "")).lower() or
            term in str(d.get("dataset_dataset", "")).lower() or
            term in str(d.get("table", "")).lower()]
    
    nations = sorted(set(d.get("Nation") for d in datasets if d.get("Nation")))
    groups = sorted(set(d.get("Group") for d in datasets if d.get("Group")))
    
    result = {
        "datasets": datasets[:100],  # Limit for performance
        "totalCount": len(datasets),
        "nations": nations,
        "groups": groups,
        "filters": {"nation": nation, "group": group, "search": search},
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Data Explorer - Explore dataset details
@mcp.tool()
async def explore_dataset(
    dataset_name: str,
    nation: str,
) -> list[TextContent]:
    """Explore detailed information about a specific dataset including coverage, completeness, and data dictionary.
    
    The dataset_name can be a user-friendly name (e.g., "HES APC", "Hospital Episode Statistics") 
    or the dataset identifier (e.g., "hes_apc"). The tool will automatically resolve it.
    """
    
    # Resolve user-friendly name to dataset identifier
    resolved_name = resolve_dataset_name(dataset_name, nation)
    if resolved_name:
        dataset_name = resolved_name
    else:
        # Return helpful error with suggestions
        datasets = DATA_CACHE.get("tre_dataset_link", [])
        if nation and nation != "All":
            datasets = [d for d in datasets if d.get("Nation") == nation]
        available = sorted(set(d.get("Shortname", "") or d.get("Title", "") for d in datasets if d.get("Shortname") or d.get("Title")))
        return [TextContent(type="text", text=f"Dataset '{dataset_name}' not found. Available datasets in {nation}: {', '.join(available[:20])}")]
    
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
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Coverage Chart - Visualize data coverage
@mcp.tool()
async def view_coverage(
    nation: str | None = None,
    dataset: str | None = None,
) -> list[TextContent]:
    """View interactive coverage charts for datasets across nations.
    
    The dataset parameter can be a user-friendly name (e.g., "HES APC", "Hospital Episode Statistics") 
    or the dataset identifier (e.g., "hes_apc"). The tool will automatically resolve it.
    """
    
    # Resolve dataset name if provided
    resolved_dataset = None
    if dataset:
        # Try to resolve with nation hint
        resolved_dataset = resolve_dataset_name(dataset, nation)
        if not resolved_dataset:
            # Try without nation filter
            resolved_dataset = resolve_dataset_name(dataset)
        if resolved_dataset:
            dataset = resolved_dataset
        else:
            # Return helpful error with suggestions
            datasets = DATA_CACHE.get("tre_dataset_link", [])
            if nation and nation != "All":
                datasets = [d for d in datasets if d.get("Nation") == nation]
            available = sorted(set(d.get("Shortname", "") or d.get("Title", "") for d in datasets if d.get("Shortname") or d.get("Title")))
            return [TextContent(type="text", text=f"Dataset '{dataset}' not found. Available datasets: {', '.join(available[:20])}")]
    
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
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Completeness Chart - Visualize data completeness
@mcp.tool()
async def view_completeness(
    nation: str | None = None,
    dataset: str | None = None,
) -> list[TextContent]:
    """View interactive completeness charts for datasets across nations.
    
    The dataset parameter can be a user-friendly name (e.g., "HES APC", "Hospital Episode Statistics") 
    or the dataset identifier (e.g., "hes_apc"). The tool will automatically resolve it.
    """
    
    # Resolve dataset name if provided
    resolved_dataset = None
    if dataset:
        # Try to resolve with nation hint
        resolved_dataset = resolve_dataset_name(dataset, nation)
        if not resolved_dataset:
            # Try without nation filter
            resolved_dataset = resolve_dataset_name(dataset)
        if resolved_dataset:
            dataset = resolved_dataset
        else:
            # Return helpful error with suggestions
            datasets = DATA_CACHE.get("tre_dataset_link", [])
            if nation and nation != "All":
                datasets = [d for d in datasets if d.get("Nation") == nation]
            available = sorted(set(d.get("Shortname", "") or d.get("Title", "") for d in datasets if d.get("Shortname") or d.get("Title")))
            return [TextContent(type="text", text=f"Dataset '{dataset}' not found. Available datasets: {', '.join(available[:20])}")]
    
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
    }
    
    return [TextContent(type="text", text=str(result))]


# Tool: Data Dictionary Explorer - Explore SDE data dictionary
@mcp.tool()
async def explore_data_dictionary(
    dataset: str,
    search: str | None = None,
) -> list[TextContent]:
    """Explore the SDE data dictionary for specific datasets with field descriptions and types.
    
    The dataset parameter can be a user-friendly name (e.g., "HES APC", "Hospital Episode Statistics") 
    or the dataset identifier (e.g., "hes_apc"). The tool will automatically resolve it.
    """
    
    # Resolve dataset name
    resolved_dataset = resolve_dataset_name(dataset)
    if resolved_dataset:
        dataset = resolved_dataset
    else:
        # Return helpful error with suggestions
        available = list(DATA_CACHE.get("sde_data_dict", {}).keys())
        return [TextContent(type="text", text=f"Dataset '{dataset}' not found in SDE data dictionary. Available datasets: {', '.join(available[:20])}")]
    
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
    }
    
    return [TextContent(type="text", text=str(stats))]


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