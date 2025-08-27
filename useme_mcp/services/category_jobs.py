import cloudscraper
import bs4
from typing import List, Optional
from .job_scraper import parse_jobs_from_html
from .category_service import get_category_by_id
from ..models import JobOffer

def fetch_category_jobs_page(category_id: int, page: int = 1, lang: str = "en", order_by: Optional[str] = None) -> List[JobOffer]:
    """Fetch jobs from a specific category page"""
    category = get_category_by_id(category_id, lang)
    if not category:
        print(f"Category {category_id} not found for language {lang}")
        return []
    
    scraper = cloudscraper.create_scraper()
    
    # Build URL with optional ordering
    url = f"https://useme.com/{lang}/jobs/category/{category.slug},{category_id}/?page={page}"
    if order_by:
        url += f"&order_by={order_by}"
    
    print(f"Fetching category jobs page {page} from {url}")
    response = scraper.get(url)
    
    # Extract HTML from <div class="jobs">
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    jobs_div = soup.find("div", class_="jobs")
    
    if not jobs_div:
        print(f"No jobs found on category page {page}")
        return []
    
    return parse_jobs_from_html(str(jobs_div))

def fetch_category_jobs_multiple_pages(category_id: int, start_page: int = 1, num_pages: int = 3, lang: str = "en", order_by: Optional[str] = None) -> List[JobOffer]:
    """Fetch jobs from multiple pages of a specific category"""
    all_jobs = []
    
    for page in range(start_page, start_page + num_pages):
        page_jobs = fetch_category_jobs_page(category_id, page, lang, order_by)
        if not page_jobs:  # Stop if no jobs found
            print(f"No more jobs found at category page {page}, stopping...")
            break
        all_jobs.extend(page_jobs)
        print(f"Found {len(page_jobs)} jobs on category page {page}")
    
    return all_jobs