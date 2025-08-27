import cloudscraper
import json
from typing import Optional
from ..models import (
    BillingResult,
    BillingCalculation,
    BillingContractor,
    BillingEmployer,
    BillingComponent,
)


def calculate_billing(
    amount: float,
    currency: str = "PLN",
    copyright_transfer: str = "license",
    contractor_country: str = "PL",
    contractor_is_business: bool = False,
    contractor_is_vat_payer: bool = False,
    employer_country: str = "PL",
    employer_is_business: bool = True,
    employer_is_vat_payer: bool = True,
) -> Optional[BillingResult]:
    """
    Calculate billing costs for Useme freelance work

    Args:
        amount: Amount to be paid out to contractor
        currency: Currency code (PLN, EUR, GBP, USD)
        copyright_transfer: "license" or "full" - whether to transfer copyrights
        contractor_country: Contractor's country code
        contractor_is_business: Whether contractor is a business
        contractor_is_vat_payer: Whether contractor pays VAT
        employer_country: Employer's country code
        employer_is_business: Whether employer is a business
        employer_is_vat_payer: Whether employer pays VAT

    Returns:
        BillingResult with detailed cost breakdown
    """
    scraper = cloudscraper.create_scraper()

    # Prepare request payload
    payload = {
        "amount": str(amount),
        "copyright_transfer": copyright_transfer,
        "currency": currency,
        "subcategory": 2,  # Default subcategory
        "billing_calculator": "N2G",  # Default billing calculator
        "contractor": {
            "email": None,
            "country": contractor_country,
            "residence": None,
            "is_business": contractor_is_business,
            "is_vat_payer": contractor_is_vat_payer,
            "user_class": "default",
        },
        "employer": {
            "email": None,
            "country": employer_country,
            "is_business": employer_is_business,
            "is_vat_payer": employer_is_vat_payer,
            "user_class": "default",
        },
        "discount": None,
        "max_income_cost": None,
    }

    try:
        print(f"Calculating billing for {amount} {currency}")

        # Make request to billing API
        response = scraper.post(
            "https://useme.com/internal-api/billing/",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            data=json.dumps(payload),
        )

        response.raise_for_status()
        data = response.json()

        # Parse response data
        billing_data = data.get("data", {})

        # Parse payin components
        payin_components = []
        for item in billing_data.get("payin", []):
            payin_components.append(
                BillingComponent(label=item["label"], value=float(item["value"]))
            )

        # Parse payout components
        payout_components = []
        for item in billing_data.get("payout", []):
            payout_components.append(
                BillingComponent(label=item["label"], value=float(item["value"]))
            )

        # Parse price components
        price_components = []
        for item in billing_data.get("priceComponents", []):
            price_components.append(
                BillingComponent(label=item["label"], value=float(item["value"]))
            )

        # Create models
        contractor = BillingContractor(
            country=contractor_country,
            is_business=contractor_is_business,
            is_vat_payer=contractor_is_vat_payer,
        )

        employer = BillingEmployer(
            country=employer_country,
            is_business=employer_is_business,
            is_vat_payer=employer_is_vat_payer,
        )

        calculation = BillingCalculation(
            currency=billing_data.get("currency", currency),
            payin=payin_components,
            payout=payout_components,
            price_components=price_components,
        )

        return BillingResult(
            amount=amount,
            currency=currency,
            copyright_transfer=copyright_transfer,
            contractor=contractor,
            employer=employer,
            calculation=calculation,
        )

    except Exception as e:
        print(f"Error calculating billing: {e}")
        return None
