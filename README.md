# BHFDSC CVD-COVID TRE Dashboard MCP Server

An interactive MCP (Model Context Protocol) server for exploring the BHFDSC CVD-COVID TRE Dashboard data. This server provides tools with interactive UI widgets for exploring datasets across England, Scotland, and Wales.

## Features

- **Dataset Picker** - Interactive picker to explore TRE datasets with filtering by nation, group, and search terms
- **Data Explorer** - Detailed exploration of specific datasets including overview, coverage, completeness, and data dictionary
- **Coverage Charts** - Interactive bar charts visualizing data coverage across nations and datasets
- **Completeness Charts** - Interactive bar charts visualizing data completeness across nations and datasets
- **Data Dictionary Explorer** - Explore SDE data dictionary with field descriptions, types, and search
- **Summary Statistics** - Overview statistics across all datasets and nations

## Data Sources

The server loads data from the [BHFDSC/cvd-covid-tre-dashboard](https://github.com/BHFDSC/cvd-covid-tre-dashboard) repository:

- **TRE Dataset Link** - Metadata for 117 datasets across England, Scotland, and Wales
- **England Data** - Overall, coverage, and completeness data (195 datasets)
- **Scotland Data** - Overview, coverage, and completeness data (15 datasets)
- **Wales (SAIL) Data** - Overview, coverage, and completeness data (24 datasets)
- **Data Dictionaries** - DD_Scotland.xlsx, DD_Wales.xlsx, and SDE Data Dictionary (65 datasets)

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone <this-repo>
cd bhfdscdashboardMCP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Running the Server

```bash
# Start the server
python mcp_server.py
```

The server will start on `http://0.0.0.0:8000/mcp` and load all data from GitHub on startup.

### Health Check

```bash
curl http://localhost:8000/health
```

## Available Tools

### `pick_dataset`
Interactive picker for TRE datasets across England, Scotland, and Wales.

**Parameters:**
- `nation` (optional): Filter by nation - "England", "Scotland", "Wales", or "All"
- `group` (optional): Filter by group (e.g., "Primary", "Secondary Care")
- `search` (optional): Search term for dataset title/description

**Returns:** Dataset metadata with interactive UI widget

### `explore_dataset`
Detailed exploration of a specific dataset.

**Parameters:**
- `dataset_name`: Name of the dataset to explore
- `nation`: Nation the dataset belongs to ("England", "Scotland", "Wales")

**Returns:** Overview, coverage, completeness, and data dictionary with interactive UI widget

### `view_coverage`
Interactive coverage charts for datasets across nations.

**Parameters:**
- `nation` (optional): Filter by nation
- `dataset` (optional): Specific dataset to view

**Returns:** Coverage data with interactive chart widget

### `view_completeness`
Interactive completeness charts for datasets across nations.

**Parameters:**
- `nation` (optional): Filter by nation
- `dataset` (optional): Specific dataset to view

**Returns:** Completeness data with interactive chart widget

### `explore_data_dictionary`
Explore the SDE data dictionary for specific datasets.

**Parameters:**
- `dataset`: Dataset name from SDE data dictionary
- `search` (optional): Search term for field names/descriptions

**Returns:** Data dictionary with interactive table widget

### `get_summary_stats`
Get summary statistics across all datasets and nations.

**Parameters:** None

**Returns:** Statistics with interactive UI widget

## Available Resources (Widgets)

- `ui://widgets/dataset-picker.html` - Dataset picker widget
- `ui://widgets/data-explorer.html` - Data explorer widget
- `ui://widgets/coverage-chart.html` - Coverage chart widget
- `ui://widgets/completeness-chart.html` - Completeness chart widget
- `ui://widgets/data-dictionary.html` - Data dictionary widget

## Configuration

Environment variables:

- `HOST` - Server host (default: "0.0.0.0")
- `PORT` - Server port (default: 8000)
- `MCP_ALLOWED_HOSTS` - Comma-separated allowed hosts for DNS rebinding protection
- `MCP_ALLOWED_ORIGINS` - Comma-separated allowed origins
- `MCP_ENABLE_DNS_REBINDING_PROTECTION` - Enable/disable DNS rebinding protection (default: true)

## Deployment on Render

```yaml
# render.yaml
services:
  - type: web
    name: bhfdsc-tre-dashboard-mcp
    env: python
    buildCommand: pip install -e .
    startCommand: python mcp_server.py
    envVars:
      - key: MCP_ALLOWED_HOSTS
        value: "*.onrender.com,localhost:*,127.0.0.1:*"
      - key: MCP_ALLOWED_ORIGINS
        value: "https://*.onrender.com"
```

## Testing with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector against local server
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

## Example Usage

```python
# Using the MCP client
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # Pick datasets from England
        result = await session.call_tool("pick_dataset", {"nation": "England"})
        
        # Explore a specific dataset
        result = await session.call_tool("explore_dataset", {
            "dataset_name": "gdppr",
            "nation": "England"
        })
        
        # View coverage charts
        result = await session.call_tool("view_coverage", {"nation": "All"})
        
        # Get summary stats
        result = await session.call_tool("get_summary_stats", {})
```

## Project Structure

```
bhfdscdashboardMCP/
├── mcp_server.py          # Main MCP server
├── pyproject.toml         # Project configuration
├── widgets/               # Interactive UI widgets
│   ├── dataset_picker.html
│   ├── data_explorer.html
│   ├── coverage_chart.html
│   ├── completeness_chart.html
│   └── data_dictionary.html
├── venv/                  # Virtual environment (gitignored)
└── README.md              # This file
```

## License

MIT License - See LICENSE file for details.