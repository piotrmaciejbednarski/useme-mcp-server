"""
Useme MCP Server - Data Fetching Tool for Freelancers on Useme Platform

This MCP server provides data fetching tools for freelancers to:
- Browse and search job offers on Useme.com
- Fetch job details and categories
- Get raw job data for LLM analysis
"""

from fastmcp import FastMCP
from typing import List, Optional, Dict, Any
import logging

# Import our services and models
from useme_mcp.services.job_scraper import (
    fetch_jobs_page,
    fetch_multiple_pages,
    fetch_job_details,
    fetch_job_competition,
)
from useme_mcp.services.category_service import (
    load_categories,
    get_category_by_id,
    find_categories_by_name,
)
from useme_mcp.services.category_jobs import (
    fetch_category_jobs_page,
    fetch_category_jobs_multiple_pages,
)
from useme_mcp.services.billing_calculator import calculate_billing
from useme_mcp.services.user_profile import fetch_user_profile

# Get system instructions
from config.instructions import SYSTEM_INSTRUCTION

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP(
    name="useme-job-assistant",
    instructions=SYSTEM_INSTRUCTION,
)


# Job Browsing Tools
@mcp.tool(
    description="""
Browse Available Job Offers from Useme Platform

Args:
- **page**: Starting page number (default: 1)
- **language**: Language version - `en` for English, `pl` for Polish (default: `en`)
- **num_pages**: Number of pages to fetch (default: 1)

Returns:
List of job offers with details like title, budget, client, and competition level.       
"""
)
def browse_jobs(
    page: int = 1,
    language: str = "en",
    num_pages: int = 1,
) -> List[Dict[str, Any]]:
    """
    Browse available job offers from Useme platform

    Args:
        page: Starting page number (default: 1)
        language: Language version - 'en' for English, 'pl' for Polish (default: 'en')
        num_pages: Number of pages to fetch (default: 1)

    Returns:
        List of job offers with details like title, budget, client, competition level
    """
    if num_pages == 1:
        jobs = fetch_jobs_page(page, language, None)
    else:
        jobs = fetch_multiple_pages(page, num_pages, language, None)

    return [job.model_dump() for job in jobs]


@mcp.tool(
    description="""
Browse Job Offers from a Specific Category

Args:
- **category_id**: Category ID (e.g., 35 for Programming/IT)
- **page**: Starting page number (default: 1)
- **language**: Language version - `en` or `pl` (default: `en`)
- **num_pages**: Number of pages to fetch (default: 1)

Returns:
List of job offers from the specified category.
"""
)
def browse_category_jobs(
    category_id: int,
    page: int = 1,
    language: str = "en",
    num_pages: int = 1,
) -> List[Dict[str, Any]]:
    """
    Browse job offers from a specific category

    Args:
        category_id: Category ID (e.g., 35 for Programming/IT)
        page: Starting page number (default: 1)
        language: Language version - 'en' or 'pl' (default: 'en')
        num_pages: Number of pages to fetch (default: 1)

    Returns:
        List of job offers from the specified category
    """
    if num_pages == 1:
        jobs = fetch_category_jobs_page(category_id, page, language, None)
    else:
        jobs = fetch_category_jobs_multiple_pages(
            category_id, page, num_pages, language, None
        )

    return [job.model_dump() for job in jobs]


# Job Filtering Tools (with order_by support)
@mcp.tool(
    description="""
Filter and Sort Job Offers from Useme Platform

Args:
- **page**: Starting page number (default: 1)
- **language**: Language version - `en` for English, `pl` for Polish (default: `en`)
- **num_pages**: Number of pages to fetch (default: 1)
- **order_by**: Sort order for jobs. Available options:
  - `-published_on`: Sort by newest jobs first
  - `expires`: Sort by jobs expiring soonest
  - `offer_count`: Sort by jobs with fewest offers
  - `-offer_count`: Sort by jobs with most offers
  - `payment_normalized`: Sort by lowest budget first
  - `-payment_normalized`: Sort by highest budget first
  - **Empty**: Default ordering (no sorting parameter)

Returns:
List of filtered and sorted job offers with details like title, budget, client, and competition level.       
"""
)
def filter_jobs(
    page: int = 1,
    language: str = "en",
    num_pages: int = 1,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter and sort available job offers from Useme platform

    Args:
        page: Starting page number (default: 1)
        language: Language version - 'en' for English, 'pl' for Polish (default: 'en')
        num_pages: Number of pages to fetch (default: 1)
        order_by: Sort order for jobs. Available options:
        - '-published_on': Sort by newest jobs first
        - 'expires': Sort by jobs expiring soonest
        - 'offer_count': Sort by jobs with fewest offers
        - '-offer_count': Sort by jobs with most offers
        - 'payment_normalized': Sort by lowest budget first
        - '-payment_normalized': Sort by highest budget first
        - Empty: Default ordering (no sorting parameter)

    Returns:
        List of filtered and sorted job offers with details like title, budget, client, competition level
    """
    if num_pages == 1:
        jobs = fetch_jobs_page(page, language, order_by)
    else:
        jobs = fetch_multiple_pages(page, num_pages, language, order_by)

    return [job.model_dump() for job in jobs]


@mcp.tool(
    description="""
Filter and Sort Job Offers from a Specific Category

Args:
- **category_id**: Category ID (e.g., 35 for Programming/IT)
- **page**: Starting page number (default: 1)
- **language**: Language version - `en` or `pl` (default: `en`)
- **num_pages**: Number of pages to fetch (default: 1)
- **order_by**: Sort order for jobs. Available options:
  - `-published_on`: Sort by newest jobs first
  - `expires`: Sort by jobs expiring soonest
  - `offer_count`: Sort by jobs with fewest offers
  - `-offer_count`: Sort by jobs with most offers
  - `payment_normalized`: Sort by lowest budget first
  - `-payment_normalized`: Sort by highest budget first
  - **Empty**: Default ordering (no sorting parameter)

Returns:
List of filtered and sorted job offers from the specified category.
"""
)
def filter_category_jobs(
    category_id: int,
    page: int = 1,
    language: str = "en",
    num_pages: int = 1,
    order_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filter and sort job offers from a specific category

    Args:
        category_id: Category ID (e.g., 35 for Programming/IT)
        page: Starting page number (default: 1)
        language: Language version - 'en' or 'pl' (default: 'en')
        num_pages: Number of pages to fetch (default: 1)
        order_by: Sort order for jobs. Available options:
        - '-published_on': Sort by newest jobs first
        - 'expires': Sort by jobs expiring soonest
        - 'offer_count': Sort by jobs with fewest offers
        - '-offer_count': Sort by jobs with most offers
        - 'payment_normalized': Sort by lowest budget first
        - '-payment_normalized': Sort by highest budget first
        - Empty: Default ordering (no sorting parameter)

    Returns:
        List of filtered and sorted job offers from the specified category
    """
    if num_pages == 1:
        jobs = fetch_category_jobs_page(category_id, page, language, order_by)
    else:
        jobs = fetch_category_jobs_multiple_pages(
            category_id, page, num_pages, language, order_by
        )

    return [job.model_dump() for job in jobs]


@mcp.tool()
def get_job_details(job_url: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific job offer

    Args:
        job_url: Full URL of the job offer

    Returns:
        Detailed job information including skills, custom fields, client info
    """
    job_detail = fetch_job_details(job_url)
    return job_detail.model_dump() if job_detail else None


@mcp.tool()
def get_job_competition(job_url: str) -> Optional[Dict[str, Any]]:
    """
    Get competition details for a specific job offer

    Analyzes competitors who have submitted offers for the job, including:
    - Username and profile information
    - Number of completed contracts (experience level)
    - Skills listed on their profiles
    - When they submitted their offers

    Args:
        job_url: Full URL of the job offer

    Returns:
        Competition analysis including list of competitors with their profiles and experience
    """
    competition = fetch_job_competition(job_url)
    return competition.model_dump() if competition else None


@mcp.tool()
def calculate_useme_billing(
    payout_amount: float,
    currency: str = "PLN",
    copyright_transfer: str = "license",
    contractor_country: str = "PL",
    contractor_is_business: bool = False,
    contractor_is_vat_payer: bool = False,
    employer_country: str = "PL",
    employer_is_business: bool = True,
    employer_is_vat_payer: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Calculate billing costs and fees for Useme freelance work

    Calculates what the client will pay (including VAT, Useme commission, PIT tax)
    based on the desired payout amount to the freelancer.

    Args:
        payout_amount: Amount the freelancer wants to receive (after all deductions)
        currency: Currency code - PLN, EUR, GBP, or USD (default: PLN)
        copyright_transfer: Transfer type - "license" (default) or "full"
        contractor_country: Freelancer's country code (default: PL)
        contractor_is_business: Whether freelancer is registered business (default: False)
        contractor_is_vat_payer: Whether freelancer pays VAT (default: False)
        employer_country: Client's country code (default: PL)
        employer_is_business: Whether client is a business (default: True)
        employer_is_vat_payer: Whether client pays VAT (default: True)

    Returns:
        Detailed breakdown of costs including:
        - Final invoice amount client pays
        - VAT amount
        - Useme commission
        - PIT tax
        - Net amount breakdown

    Example:
        250 PLN payout → 362.85 PLN total client payment
        (295 PLN base + 67.85 PLN VAT, minus 29 PLN commission + 16 PLN PIT)
    """
    billing = calculate_billing(
        amount=payout_amount,
        currency=currency,
        copyright_transfer=copyright_transfer,
        contractor_country=contractor_country,
        contractor_is_business=contractor_is_business,
        contractor_is_vat_payer=contractor_is_vat_payer,
        employer_country=employer_country,
        employer_is_business=employer_is_business,
        employer_is_vat_payer=employer_is_vat_payer,
    )
    return billing.model_dump() if billing else None


@mcp.tool()
def get_user_profile(profile_url: str) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive user profile information from Useme

    Analyzes a freelancer's public profile to understand their background,
    experience, and reputation. Perfect for competitive analysis.

    Args:
        profile_url: Full URL to the user's Useme profile
                    (e.g., https://useme.com/pl/roles/contractor/username,123456/)

    Returns:
        Detailed profile information including:
        - Basic info: username, location, registration date
        - Performance stats: completed deals, success rate, opinions
        - Professional info: categories, skills, portfolio projects
        - Social proof: client reviews and freelancer responses
        - Work history: completed projects with descriptions
    """
    profile = fetch_user_profile(profile_url)
    return profile.model_dump() if profile else None


# Category Management Tools
@mcp.tool()
def list_categories(language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List available job categories

    Args:
        language: Filter by language ('en' or 'pl'). If None, returns all categories

    Returns:
        List of available categories with their IDs and names
    """
    categories = load_categories(language)
    return [cat.model_dump() for cat in categories]


@mcp.tool()
def search_categories(
    search_term: str, language: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for categories by name

    Args:
        search_term: Term to search for in category names
        language: Optional language filter ('en' or 'pl')

    Returns:
        List of matching categories
    """
    categories = find_categories_by_name(search_term, language)
    return [cat.model_dump() for cat in categories]


@mcp.tool()
def get_category_info(
    category_id: int, language: str = "en"
) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific category

    Args:
        category_id: ID of the category
        language: Language version ('en' or 'pl')

    Returns:
        Category information including name, slug, and parent category if applicable
    """
    category = get_category_by_id(category_id, language)
    return category.model_dump() if category else None


if __name__ == "__main__":
    mcp.run()
