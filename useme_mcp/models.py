from typing import Optional, List
from pydantic import BaseModel, field_validator
from decimal import Decimal
import re


class Category(BaseModel):
    name: str
    slug: str
    category_id: int
    lang: str


class JobOffer(BaseModel):
    client: str
    offers_count: int
    days_left: int
    title: str
    description: str
    category: str
    tags: List[str] = []
    budget: str
    negotiable: bool = False
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    deals_count: Optional[int] = None
    url: str


class JobDetail(BaseModel):
    title: str
    client: str
    description: str
    published_ago: str
    category: str
    copyright: str
    skills: List[str] = []
    budget: str
    negotiable: bool = False
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    valid_for: str
    offers_count: int
    url: str
    custom_fields: dict = {}

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, v, info):
        if info.data is None:
            return v
        budget = info.data.get("budget", "")
        if budget == "Negotiable":
            return None

        # Extract price and currency
        price_match = re.search(r"([\d,]+\.?\d*)\s*([A-Z]{3})", budget)
        if price_match:
            amount_str = price_match.group(1).replace(",", "")
            return Decimal(amount_str)
        return None

    @field_validator("currency", mode="before")
    @classmethod
    def parse_currency(cls, v, info):
        if info.data is None:
            return v
        budget = info.data.get("budget", "")
        price_match = re.search(r"([\d,]+\.?\d*)\s*([A-Z]{3})", budget)
        if price_match:
            return price_match.group(2)
        return None

    @field_validator("negotiable", mode="before")
    @classmethod
    def parse_negotiable(cls, v, info):
        if info.data is None:
            return v
        budget = info.data.get("budget", "")
        return budget == "Negotiable"


class JobCompetitor(BaseModel):
    username: str
    profile_url: str
    contracts_completed: Optional[int] = None
    skills: List[str] = []
    submitted_time: str


class JobCompetition(BaseModel):
    job_url: str
    job_id: str
    total_offers: int
    total_pages: int
    competitors: List[JobCompetitor] = []


class BillingContractor(BaseModel):
    email: Optional[str] = None
    country: str = "PL"
    residence: Optional[str] = None
    is_business: bool = False
    is_vat_payer: bool = False
    user_class: str = "default"


class BillingEmployer(BaseModel):
    email: Optional[str] = None
    country: str = "PL"
    is_business: bool = True
    is_vat_payer: bool = True
    user_class: str = "default"


class BillingComponent(BaseModel):
    label: str
    value: float


class BillingCalculation(BaseModel):
    currency: str
    payin: List[BillingComponent] = []
    payout: List[BillingComponent] = []
    price_components: List[BillingComponent] = []


class BillingResult(BaseModel):
    amount: float
    currency: str
    copyright_transfer: str
    contractor: BillingContractor
    employer: BillingEmployer
    calculation: BillingCalculation
