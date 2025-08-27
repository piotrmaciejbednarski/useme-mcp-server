import cloudscraper
import bs4
import re
from typing import Optional, List
from ..models import JobOffer, JobDetail, JobCompetitor, JobCompetition


def parse_jobs_from_html(html_content: str) -> List[JobOffer]:
    """Parse job offers from HTML content"""
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    jobs = []

    # Find all job articles
    job_articles = soup.find_all("article", class_="job")

    for article in job_articles:
        try:
            # Extract client name
            client_elem = article.find("strong")
            client = client_elem.get("aria-label", "").strip() if client_elem else ""

            # Extract deals count (optional) - support both English and Polish
            deals_elem = article.find(
                "span", string=re.compile(r"\d+\s+(deal|umów|umowa)")
            )
            deals_count = None
            if deals_elem:
                deals_match = re.search(r"(\d+)", deals_elem.text)
                if deals_match:
                    deals_count = int(deals_match.group(1))

            # Extract offers count
            offers_span = article.find(
                "div", class_="job__header-details--offers"
            ).find("span", string=re.compile(r"\d+"))
            offers_count = int(offers_span.text.strip()) if offers_span else 0

            # Extract days left (support both English and Polish)
            days_span = article.find("div", class_="job__header-details--date").find(
                "span", string=re.compile(r"(\d+ days? left|\d+ dni|Znika za \d+ dni)")
            )
            days_left = 0
            if days_span:
                # Handle both "X days left", "Znika za X dni", and "X dni" formats
                days_match = re.search(r"(\d+)", days_span.text)
                if days_match:
                    days_left = int(days_match.group(1))

            # Extract title and URL
            title_link = article.find("a", class_="job__title-link")
            title = title_link.text.strip() if title_link else ""

            # Extract job URL
            job_url = ""
            if title_link and title_link.get("href"):
                href = title_link.get("href")
                # Make sure it's a complete URL
                if href.startswith("/"):
                    job_url = f"https://useme.com{href}"
                else:
                    job_url = href

            # Extract description
            desc_p = article.find("p", class_="mb-0 pb-0")
            description = desc_p.text.strip() if desc_p else ""

            # Extract category
            category_p = article.find("div", class_="job__category").find("p")
            category = category_p.text.strip() if category_p else ""

            # Extract tags
            tag_links = article.find_all("a", class_="tag--jobs")
            tags = [tag.text.strip() for tag in tag_links]

            # Extract budget - support both English and Polish
            budget_span = article.find("span", class_="job__budget-value")
            budget = budget_span.text.strip() if budget_span else "Negotiable"
            # Normalize "Do negocjacji" to "Negotiable" for consistent processing
            if budget == "Do negocjacji":
                budget = "Negotiable"

            # Create job offer
            job = JobOffer(
                client=client,
                offers_count=offers_count,
                days_left=days_left,
                title=title,
                description=description,
                category=category,
                tags=tags,
                budget=budget,
                deals_count=deals_count,
                url=job_url,
            )

            jobs.append(job)

        except Exception as e:
            print(f"Error parsing job: {e}")
            continue

    return jobs


def fetch_jobs_page(
    page: int = 1, lang: str = "en", order_by: Optional[str] = None
) -> List[JobOffer]:
    """Fetch jobs from a specific page"""
    scraper = cloudscraper.create_scraper()

    # Build URL with optional ordering
    url = f"https://useme.com/{lang}/jobs/?page={page}"
    if order_by:
        url += f"&order_by={order_by}"

    print(f"Fetching page {page} from {url}")
    response = scraper.get(url)

    # Extract HTML from <div class="jobs">
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    jobs_div = soup.find("div", class_="jobs")

    if not jobs_div:
        print(f"No jobs found on page {page}")
        return []

    return parse_jobs_from_html(str(jobs_div))


def fetch_multiple_pages(
    start_page: int = 1,
    num_pages: int = 3,
    lang: str = "en",
    order_by: Optional[str] = None,
) -> List[JobOffer]:
    """Fetch jobs from multiple pages"""
    all_jobs = []

    for page in range(start_page, start_page + num_pages):
        page_jobs = fetch_jobs_page(page, lang, order_by)
        if not page_jobs:  # Stop if no jobs found
            print(f"No more jobs found at page {page}, stopping...")
            break
        all_jobs.extend(page_jobs)
        print(f"Found {len(page_jobs)} jobs on page {page}")

    return all_jobs


def parse_job_detail_from_html(html_content: str, job_url: str) -> Optional[JobDetail]:
    """Parse detailed job information from jobs-page__content HTML"""
    soup = bs4.BeautifulSoup(html_content, "html.parser")

    try:
        # Extract title
        title_elem = soup.find("h1", class_="jobs__page-title")
        title = title_elem.text.strip() if title_elem else ""

        # Extract client name - will be updated from summary items
        client = ""

        # Extract description
        desc_elem = soup.find("div", class_="jobs-summary__item-text")
        description = ""
        if desc_elem:
            paragraphs = desc_elem.find_all("p")
            description = " ".join([p.text.strip() for p in paragraphs])

        # Find all summary items
        summary_items = soup.find_all("div", class_="jobs-summary__item")

        published_ago = ""
        category = ""
        copyright = ""
        budget = "Negotiable"
        valid_for = ""
        skills = []
        offers_count = 0
        custom_fields = {}

        for item in summary_items:
            label_elem = item.find("div", class_="jobs-summary__item-label")

            # Check both jobs-summary__item-value and jobs-summary__item-text
            value_elem = item.find(
                "div", class_="jobs-summary__item-value"
            ) or item.find("div", class_="jobs-summary__item-text")

            if not label_elem or not value_elem:
                continue

            label = label_elem.text.strip()

            # Check if there's a link with class "filename" in the value element
            link_elem = value_elem.find("a", class_="filename")
            if link_elem and link_elem.get("href"):
                href = link_elem.get("href")
                # Make sure it's a complete URL
                if href.startswith("/"):
                    value = f"https://useme.com{href}"
                else:
                    value = href
            else:
                value = value_elem.text.strip()

            if label in ["Zleceniodawca", "Employer"]:
                # For client, we want the text, not the URL
                client = value_elem.text.strip()
            elif label in ["Opublikowano", "Published"]:
                published_ago = value
            elif label in ["Kategoria", "Category"]:
                category_link = value_elem.find("a")
                category = (
                    category_link.text.strip()
                    if category_link
                    else value_elem.text.strip()
                )
            elif label in ["Prawa autorskie", "Copyright"]:
                copyright = value
            elif label in ["Budżet", "Budget"]:
                budget = value
                if budget == "Do negocjacji":
                    budget = "Negotiable"
            elif label in ["Ważne przez", "Valid for", "Expires in"]:
                valid_for = value
            elif label in ["Umiejętności", "Skills"]:
                skill_links = value_elem.find_all("a")
                skills = [link.text.strip() for link in skill_links]
            else:
                # Store any other custom fields
                custom_fields[label] = value

        # Extract offers count from offers section (both Polish and English)
        offers_header = soup.find(
            "h3", string=re.compile(r"(Wysłane oferty|Submitted offers)")
        )
        if offers_header:
            offers_match = re.search(r"\((\d+)\)", offers_header.text)
            if offers_match:
                offers_count = int(offers_match.group(1))

        return JobDetail(
            title=title,
            client=client,
            description=description,
            published_ago=published_ago,
            category=category,
            copyright=copyright,
            skills=skills,
            budget=budget,
            valid_for=valid_for,
            offers_count=offers_count,
            url=job_url,
            custom_fields=custom_fields,
        )

    except Exception as e:
        print(f"Error parsing job detail: {e}")
        return None


def fetch_job_details(job_url: str) -> Optional[JobDetail]:
    """Fetch and parse detailed job information from job URL"""
    scraper = cloudscraper.create_scraper()
    print(f"Fetching job details from: {job_url}")

    try:
        response = scraper.get(job_url)
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # Find the jobs-page__content div
        content_div = soup.find("div", class_="jobs-page__content row")

        if content_div:
            return parse_job_detail_from_html(str(content_div), job_url)
        else:
            print("Could not find jobs-page__content div")
            return None

    except Exception as e:
        print(f"Error fetching job details: {e}")
        return None


def extract_job_id_from_url(job_url: str) -> Optional[str]:
    """Extract job ID from Useme job URL"""
    # Handle various URL formats
    # https://useme.com/pl/jobs/nazwa-oferty,123456/
    # https://useme.com/en/jobs/job-name,123456/

    import re

    # Look for pattern with comma and numbers
    match = re.search(r",(\d+)/?$", job_url)
    if match:
        return match.group(1)

    # Fallback: look for any sequence of digits at the end
    match = re.search(r"/(\d+)/?$", job_url)
    if match:
        return match.group(1)

    return None


def fetch_competition_page(
    job_id: str, page: int = 1, lang: str = "pl"
) -> Optional[dict]:
    """Fetch single page of competition data from API"""
    scraper = cloudscraper.create_scraper()

    # Build API URL
    api_url = f"https://useme.com/{lang}/jobs/get-offers/{job_id}/"
    if page > 1:
        api_url += f"?page={page}"

    print(f"Fetching competition page {page} from: {api_url}")

    try:
        response = scraper.get(api_url)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        print(f"Error fetching competition page {page}: {e}")
        return None


def parse_competition_from_api_data(
    api_data: dict, job_url: str, job_id: str
) -> JobCompetition:
    """Parse competition data from API response"""
    competitors = []

    for result in api_data.get("results", []):
        try:
            # Extract username
            username = result.get("contractor_user", "")

            # Extract profile URL
            profile_url = result.get("contractor_url", "")

            # Extract contracts completed
            contracts_completed = result.get("contractor_deals")
            if contracts_completed is not None:
                contracts_completed = int(contracts_completed)

            # Extract skills from contractor_tags
            skills = []
            contractor_tags = result.get("contractor_tags", [])
            for tag in contractor_tags:
                if isinstance(tag, dict) and "name" in tag:
                    skills.append(tag["name"])

            # Extract submission time
            submitted_time = result.get("created_on", "")

            competitor = JobCompetitor(
                username=username,
                profile_url=profile_url,
                contracts_completed=contracts_completed,
                skills=skills,
                submitted_time=submitted_time,
            )

            competitors.append(competitor)

        except Exception as e:
            print(f"Error parsing competitor from API data: {e}")
            continue

    # Calculate total offers from all competitors found
    total_offers = len(competitors)
    total_pages = api_data.get("total_pages", 1)

    return JobCompetition(
        job_url=job_url,
        job_id=job_id,
        total_offers=total_offers,
        total_pages=total_pages,
        competitors=competitors,
    )


def fetch_job_competition(job_url: str) -> Optional[JobCompetition]:
    """Fetch and parse competition data from a job URL using API"""
    print(f"Fetching job competition from: {job_url}")

    # Extract job ID from URL
    job_id = extract_job_id_from_url(job_url)
    if not job_id:
        print(f"Could not extract job ID from URL: {job_url}")
        return JobCompetition(
            job_url=job_url, job_id="", total_offers=0, total_pages=0, competitors=[]
        )

    # Determine language from URL
    lang = "pl" if "/pl/" in job_url else "en"

    try:
        # Fetch first page to get total pages
        first_page_data = fetch_competition_page(job_id, 1, lang)
        if not first_page_data:
            return JobCompetition(
                job_url=job_url,
                job_id=job_id,
                total_offers=0,
                total_pages=0,
                competitors=[],
            )

        total_pages = first_page_data.get("total_pages", 1)
        all_competitors = []

        # Parse first page
        first_page_competition = parse_competition_from_api_data(
            first_page_data, job_url, job_id
        )
        all_competitors.extend(first_page_competition.competitors)

        # Fetch remaining pages if any
        for page in range(2, total_pages + 1):
            page_data = fetch_competition_page(job_id, page, lang)
            if page_data:
                page_competition = parse_competition_from_api_data(
                    page_data, job_url, job_id
                )
                all_competitors.extend(page_competition.competitors)
            else:
                print(f"Failed to fetch page {page}, continuing with partial data")

        return JobCompetition(
            job_url=job_url,
            job_id=job_id,
            total_offers=len(all_competitors),
            total_pages=total_pages,
            competitors=all_competitors,
        )

    except Exception as e:
        print(f"Error fetching job competition: {e}")
        return JobCompetition(
            job_url=job_url,
            job_id=job_id,
            total_offers=0,
            total_pages=0,
            competitors=[],
        )
