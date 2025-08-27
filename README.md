# Useme MCP Server

MCP (Model Context Protocol) server providing data fetching tools for the [Useme.com](https://useme.com) freelance platform. This server allows AI assistants to help freelancers find and analyze job opportunities.

## Features

The server provides pure data fetching tools - all analysis and recommendations are handled by the LLM:

- **Job browsing**: Fetch jobs from main pages or specific categories
- **Detailed job info**: Get comprehensive job details including skills, budget, client info
- **Category management**: List and search available job categories
- **Multi-language support**: Support for Polish and English versions of Useme

## Quick Start

### Prerequisites
- Python 3.8+
- [UV](https://docs.astral.sh/uv/) (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/piotrmaciejbednarski/useme-mcp-server.git
```

2. Add to your MCP client configuration (e.g. Claude Desktop):

```json
{
  "mcpServers": {
    "useme-job-assistant": {
        "type": "stdio",
        "command": "uvx",
        "args": [
            "--with", "cloudscraper,pydantic,beautifulsoup4",
            "fastmcp", "run",
            "/absolute/path/to/useme-mcp-server/server.py"
        ]
    }
  }
}
```

## Available Tools

### Job Browsing

- `browse_jobs(page, language = "en", num_pages)` - Browse job offers from main pages (default ordering)
- `browse_category_jobs(category_id, page, language = "en", num_pages)` - Browse jobs from specific categories (default ordering)
- `get_job_details(job_url)` - Get detailed information about a specific job
- `get_job_competition(job_url)` - Analyze competition for a specific job offer

### Job Filtering & Sorting

- `filter_jobs(page, language = "en", num_pages, order_by)` - Filter and sort job offers with custom ordering
- `filter_category_jobs(category_id, page, language = "en", num_pages, order_by)` - Filter and sort jobs from specific categories

**Sorting options for filter functions:**

- `-published_on`: Sort by newest jobs first
- `expires`: Sort by jobs expiring soonest  
- `offer_count`: Sort by jobs with fewest offers
- `-offer_count`: Sort by jobs with most offers
- `payment_normalized`: Sort by lowest budget first
- `-payment_normalized`: Sort by highest budget first

### Category Management

- `list_categories(language = "en")` - List available job categories
- `search_categories(search_term, language = "en")` - Search categories by name
- `get_category_info(category_id, language = "en")` - Get info about specific category

## Example usage

### Basic browsing

```md
**User:** Show me recent job offers from Programming category. Only polish offers.

**Assistant:** Ran `search_categories(search_term='programowanie', language='pl')`

**Assistant:** Ran `browse_category_jobs(category_id=35, page=1, language='pl', num_pages=2)`
```

### Filtering and sorting

```md
**User:** Find highest paying Python jobs from last week, sorted by budget. Only polish offers.

**Assistant:** Ran `search_categories(search_term='programowanie', language='pl')`

**Assistant:** Ran `filter_category_jobs(category_id=35, page=1, language='pl', num_pages=3, order_by='-payment_normalized')`

**Assistant:** Found job offers for Python developer sorted by highest budget first:

...

**User:** Check details for the top offers.

**Assistant:** Ran `get_job_details(job_url_1)`

**Assistant:** Ran `get_job_details(job_url_2)`

...

**Assistant:** Based on the offer details, I recommend applying for Offer 1 because it has competitive budget and reasonable requirements.
```

### Competition analysis

```md
**User:** Analyze the competition for this job offer to help me decide if I should apply.

**Assistant:** Ran `get_job_competition(job_url='https://useme.com/pl/job/123456/')`

**Assistant:** Competition analysis shows:
- **12 total competitors** have submitted offers
- **Experience levels:** 3 experienced (50+ contracts), 6 intermediate (5-20 contracts), 3 beginners (0-2 contracts)
- **Common skills:** Most competitors have Python, Django, but few have machine learning experience
- **Submission timing:** Most offers submitted today

**Recommendation:** Good opportunity to apply - you have unique ML skills that most competitors lack, and there's reasonable competition level.
```