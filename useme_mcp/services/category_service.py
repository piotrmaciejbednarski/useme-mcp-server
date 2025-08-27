import json
from typing import Optional, List
from pathlib import Path
from ..models import Category


def load_categories(lang: Optional[str] = None) -> List[Category]:
    """Load categories from static JSON file, optionally filtered by language"""
    try:
        categories_file = (
            Path(__file__).parent.parent.parent / "data" / "categories.json"
        )
        with open(categories_file, "r", encoding="utf-8") as f:
            categories_data = json.load(f)

        categories = [Category(**cat_data) for cat_data in categories_data]

        if lang:
            categories = [cat for cat in categories if cat.lang == lang]

        return categories
    except FileNotFoundError:
        print("categories.json not found.")
        return []


def get_category_by_id(category_id: int, lang: str = "en") -> Optional[Category]:
    """Get category by ID and language"""
    categories = load_categories(lang)
    for category in categories:
        if category.category_id == category_id:
            return category
    return None


def get_all_categories() -> List[Category]:
    """Get all available categories"""
    return load_categories()


def get_categories_by_language(lang: str) -> List[Category]:
    """Get categories for specific language"""
    return load_categories(lang)


def find_categories_by_name(
    search_term: str, lang: Optional[str] = None
) -> List[Category]:
    """Find categories by name (partial match)"""
    categories = load_categories(lang)
    search_term = search_term.lower()

    return [
        cat
        for cat in categories
        if search_term in cat.name.lower() or search_term in cat.slug.lower()
    ]
