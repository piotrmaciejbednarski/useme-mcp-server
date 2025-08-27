# Useme MCP Server

MCP (Model Context Protocol) server providing data fetching tools for the [Useme.com](https://useme.com) freelance platform. This server allows AI assistants to help freelancers find and analyze job opportunities.

## Features

The server provides pure data fetching tools - all analysis and recommendations are handled by the LLM:

- **Job browsing**: Fetch jobs from main pages or specific categories
- **Detailed job info**: Get comprehensive job details including skills, budget, client info
- **Category management**: List and search available job categories
- **Multi-language support**: Support for Polish and English versions of Useme

## Installation

Clone this repo using `git` then add the MCP server to your configuration:

```json
{
  "mcpServers": {
    "useme-job-assistant": {
        "type": "stdio",
        "command": "uvx",
        "args": [
            "--with",
            "cloudscraper,pydantic,beautifulsoup4",
            "fastmcp",
            "run",
            "{absolute_path}/useme-mcp-server/server.py"
        ]
    }
  }
}
```

Replace `{absolute_path}` with the absolute path to your repository.

Remember to install UV in the operating system (https://docs.astral.sh/uv/getting-started/installation/), without it, you won't be able to use `uvx`.

## Available Tools

### Job Browsing

- `browse_jobs(page, language = "en", num_pages)` - Browse job offers from main pages
- `browse_category_jobs(category_id, page, language = "en", num_pages)` - Browse jobs from specific categories
- `get_job_details(job_url)` - Get detailed information about a specific job

### Category Management

- `list_categories(language = "en")` - List available job categories
- `search_categories(search_term, language = "en")` - Search categories by name
- `get_category_info(category_id, language = "en")` - Get info about specific category

## Example usage

```md
**User:** Fetch last 2 pages of job offers from Useme in Polish language for Programming category. Then find a job offer for Python developer.

**Assistant:** Ran `search_categories(search_term='programowanie', language='pl')`

**Assistant:** Ran `browse_category_jobs(category_id=35, page=1, language='pl', num_pages=2)`

**Assistant:** Found job offers for Python developer:

...

**User:** Check details for this offers, and tell me which one is the best fit for me. I'm just starting out as a Python developer.

**Assistant:** Ran `get_job_details(job_url_1)`

**Assistant:** Ran `get_job_details(job_url_2)`

...

**Assistant:** Based on the offer details, I recommend applying for Offer 1 because it has a lower competition level and a reasonable budget for entry-level developers.

**User:** Thanks. Write me proposal message for this offer.

**Assistant:** Sure! Here's a proposal message you can use:

...
```