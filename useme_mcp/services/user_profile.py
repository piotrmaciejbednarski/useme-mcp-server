import cloudscraper
import bs4
import re
from typing import Optional
from ..models import (
    UserProfile,
    UserProfileStats,
    UserDeals,
    UserOpinions,
    UserCategory,
    UserPortfolioItem,
    UserOpinion,
    UserCompletedJob,
)


def parse_user_profile_from_html(
    html_content: str, profile_url: str
) -> Optional[UserProfile]:
    """Parse user profile data from public_user_profile HTML content"""
    soup = bs4.BeautifulSoup(html_content, "html.parser")

    try:
        # Extract username
        username_elem = soup.find("h1", class_="profile-main__user-data-name")
        username = username_elem.text.strip() if username_elem else ""

        # Parse profile stats (country, location, useme since)
        stats_div = soup.find("div", class_="profile-stats")
        country = ""
        location = None
        useme_since = ""

        if stats_div:
            # Find country - text is directly in paragraph, not in strong tags
            for p in stats_div.find_all("p"):
                p_text = p.get_text()
                if "From:" in p_text or "Kraj:" in p_text:
                    # Extract country from span with class accent accent--black
                    country_span = p.find("span", class_="accent accent--black")
                    if country_span:
                        country = country_span.text.strip()
                elif "Location:" in p_text or "Lokalizacja:" in p_text:
                    # Extract location from span with class accent accent--black
                    location_span = p.find("span", class_="accent accent--black")
                    if location_span:
                        location = location_span.text.strip()
                elif "On Useme since" in p_text or "Na Useme od" in p_text:
                    # For registration date, extract the full text after the prefix
                    if "On Useme since" in p_text:
                        useme_since = p_text.replace("On Useme since", "").strip()
                    elif "Na Useme od" in p_text:
                        useme_since = p_text.replace("Na Useme od", "").strip()

        profile_stats = UserProfileStats(
            country=country, location=location, useme_since=useme_since
        )

        # Parse deals statistics
        deals_div = soup.find("div", class_="profile-main__user-data__deals")
        total_deals = 0
        successful = 0
        disputed = 0
        failed = 0

        if deals_div:
            # Extract total deals from title - look for span with class accent accent--grey
            deals_title = deals_div.find("h2", class_="profile-main__title-secondary")
            if deals_title:
                grey_span = deals_title.find("span", class_="accent accent--grey")
                if grey_span:
                    total_deals = int(grey_span.text.strip())

            # Extract individual stats
            deals_stats = deals_div.find("div", class_="profile-stats")
            if deals_stats:
                for p in deals_stats.find_all("p"):
                    text = p.text.strip()
                    if "SUCCESSFUL:" in text or "ZAKOŃCZONE:" in text:
                        # Extract number from span with class accent accent--green
                        green_span = p.find("span", class_="accent accent--green")
                        if green_span:
                            successful = int(green_span.text.strip())
                    elif "DISPUTED:" in text or "SPORNE:" in text:
                        # Extract number from span with class accent accent--yellow
                        yellow_span = p.find("span", class_="accent accent--yellow")
                        if yellow_span:
                            disputed = int(yellow_span.text.strip())
                    elif "FAILED:" in text or "ZERWANE:" in text:
                        # Extract number from span with class accent accent--red
                        red_span = p.find("span", class_="accent accent--red")
                        if red_span:
                            failed = int(red_span.text.strip())

        user_deals = UserDeals(
            total=total_deals, successful=successful, disputed=disputed, failed=failed
        )

        # Parse opinions statistics
        opinions_div = soup.find("div", class_="profile-main__user-data__opinions")
        total_opinions = 0
        positive = 0
        neutral = 0
        negative = 0

        if opinions_div:
            # Extract total opinions from title
            opinions_title = opinions_div.find(
                "h2", class_="profile-main__title-secondary"
            )
            if opinions_title:
                opinions_match = re.search(r"(\d+)", opinions_title.text)
                if opinions_match:
                    total_opinions = int(opinions_match.group(1))

            # Extract individual stats
            opinions_stats = opinions_div.find("div", class_="profile-stats")
            if opinions_stats:
                for p in opinions_stats.find_all("p"):
                    text = p.text.strip()
                    if "POSITIVE:" in text or "POZYTYWNE:" in text:
                        match = re.search(r"(\d+)", text)
                        if match:
                            positive = int(match.group(1))
                    elif "NEUTRAL:" in text or "NEUTRALNE:" in text:
                        match = re.search(r"(\d+)", text)
                        if match:
                            neutral = int(match.group(1))
                    elif "NEGATIVE:" in text or "NEGATYWNE:" in text:
                        match = re.search(r"(\d+)", text)
                        if match:
                            negative = int(match.group(1))

        user_opinions_stats = UserOpinions(
            total=total_opinions, positive=positive, neutral=neutral, negative=negative
        )

        # Parse "About me" section
        about_me = None
        about_div = soup.find("div", class_="profile-main__about_me")
        if about_div:
            about_p = about_div.find("p")
            if about_p:
                about_me = about_p.text.strip()

        # Parse categories
        categories = []
        categories_divs = soup.find_all("div", class_="profile-main__cat-tree")
        for cat_div in categories_divs:
            category_links = cat_div.find_all("a")
            if len(category_links) >= 1:
                main_cat = category_links[0]
                sub_cat = category_links[1] if len(category_links) > 1 else None

                if sub_cat:
                    # Subcategory with parent
                    category = UserCategory(
                        name=f"{main_cat.text.strip()} > {sub_cat.text.strip()}"
                    )
                else:
                    # Main category only
                    category = UserCategory(name=main_cat.text.strip())
                categories.append(category)

        # Parse skills/tags
        skills = []
        tags_div = soup.find("div", class_="profile-main__tags")
        if tags_div:
            skill_links = tags_div.find_all("a", class_="tag")
            skills = [link.text.strip() for link in skill_links]

        # Parse portfolio
        portfolio = []
        portfolio_div = soup.find("div", class_="profile-main__portfolio")
        if portfolio_div:
            portfolio_items = portfolio_div.find_all(
                "div", class_="profile-main__portfolio__item"
            )
            for item in portfolio_items:
                title = ""
                url = ""
                description = ""

                # Look for external link first (with target="_blank")
                external_link = item.find("a", {"target": "_blank"})
                if external_link:
                    title = external_link.text.strip()
                    url = external_link.get("href", "")
                else:
                    # Look for h6 title (for items without external links)
                    title_h6 = item.find("h6")
                    if title_h6:
                        title = title_h6.text.strip()

                # Get description from p tag
                desc_p = item.find("p")
                if desc_p:
                    description = desc_p.text.strip()

                if title:  # Only add if we found a title
                    portfolio_item = UserPortfolioItem(
                        title=title, url=url, description=description
                    )
                    portfolio.append(portfolio_item)

        # Parse user opinions
        user_opinions = []
        opinions_section = soup.find("div", class_="profile-main__opinions")
        if opinions_section:
            opinion_rows = opinions_section.find_all("div", class_="row opinion")
            for row in opinion_rows:
                try:
                    # Extract author info
                    portrait = row.find("div", class_="portrait")
                    author_name = ""
                    date = ""

                    if portrait:
                        name_span = portrait.find("span", class_="portrait__name")
                        author_name = name_span.text.strip() if name_span else ""

                        date_div = portrait.find("div", class_="portrait__date")
                        if date_div:
                            date = (
                                date_div.text.strip()
                                .replace("on ", "")
                                .replace("w dniu ", "")
                            )

                    # Extract opinion type
                    opinion_type = "neutral"
                    if row.find("div", class_="opinion-type-positive"):
                        opinion_type = "positive"
                    elif row.find("div", class_="opinion-type-negative"):
                        opinion_type = "negative"

                    # Extract opinion content
                    content = ""
                    content_div = row.find("div", class_="opinion-content-text")
                    if content_div:
                        content = content_div.text.strip()

                    # Extract freelancer reply if exists
                    freelancer_reply = None
                    freelancer_reply_date = None
                    answer_div = row.find("div", class_="opinion-content-answer")
                    if answer_div:
                        reply_content = answer_div.find(
                            "div", class_="opinion-content-text"
                        )
                        if reply_content:
                            freelancer_reply = reply_content.text.strip()

                        reply_portrait = answer_div.find("div", class_="portrait")
                        if reply_portrait:
                            reply_date_div = reply_portrait.find(
                                "div", class_="portrait__date"
                            )
                            if reply_date_div:
                                freelancer_reply_date = (
                                    reply_date_div.text.strip()
                                    .replace("on ", "")
                                    .replace("w dniu ", "")
                                )

                    opinion = UserOpinion(
                        author_name=author_name,
                        date=date,
                        opinion_type=opinion_type,
                        content=content,
                        freelancer_reply=freelancer_reply,
                        freelancer_reply_date=freelancer_reply_date,
                    )
                    user_opinions.append(opinion)

                except Exception as e:
                    print(f"Error parsing opinion: {e}")
                    continue

        # Parse completed jobs
        completed_jobs = []
        completed_section = soup.find("ul", class_="recent-jobs__list")
        if completed_section:
            job_items = completed_section.find_all(
                "li", class_="recent-jobs__list-item"
            )
            for item in job_items:
                try:
                    title_link = item.find("a", class_="recent-job__title")
                    desc_div = item.find("div", class_="recent-job__description")
                    category_link = item.find("a", class_="recent-job__category")

                    if title_link and category_link:
                        category_name_span = category_link.find(
                            "span", class_="recent-job__category-name"
                        )

                        job = UserCompletedJob(
                            title=title_link.text.strip(),
                            url=title_link.get("href", ""),
                            description=desc_div.text.strip() if desc_div else "",
                            category_name=category_name_span.text.strip()
                            if category_name_span
                            else "",
                        )
                        completed_jobs.append(job)

                except Exception as e:
                    print(f"Error parsing completed job: {e}")
                    continue

        return UserProfile(
            profile_url=profile_url,
            username=username,
            stats=profile_stats,
            deals=user_deals,
            opinions=user_opinions_stats,
            about_me=about_me,
            categories=categories,
            skills=skills,
            portfolio=portfolio,
            user_opinions=user_opinions,
            completed_jobs=completed_jobs,
        )

    except Exception as e:
        print(f"Error parsing user profile: {e}")
        return None


def fetch_user_profile(profile_url: str) -> Optional[UserProfile]:
    """Fetch and parse user profile data from profile URL"""
    scraper = cloudscraper.create_scraper()
    print(f"Fetching user profile from: {profile_url}")

    try:
        response = scraper.get(profile_url)
        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # Find the public_user_profile div
        profile_div = soup.find("div", id="public_user_profile")

        if profile_div:
            return parse_user_profile_from_html(str(profile_div), profile_url)
        else:
            print("Could not find public_user_profile div")
            return None

    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None
