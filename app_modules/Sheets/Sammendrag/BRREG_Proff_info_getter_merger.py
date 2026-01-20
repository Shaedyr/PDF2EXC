from app_modules.Sheets.Sammendrag.BRREG_info_getter import fetch_company_by_org, format_company_data
from app_modules.Sheets.Sammendrag.proff_info_getter import get_proff_data


def merge_company_data(org_number: str) -> dict:
    """
    Fetches BRREG + Proff data for a company and merges them.
    - BRREG is primary source (identity, address, NACE, employees).
    - Proff always overrides revenue_2024.
    - Proff fills missing fields.
    - Proff adds financials.
    """

    BRREG_data = format_company_data(fetch_company_by_org(org_number)) or {}
    proff_data = get_proff_data(org_number) or {}

    merged = BRREG_data.copy()

    # Always prefer Proff revenue
    if proff_data.get("revenue_2024"):
        merged["revenue_2024"] = proff_data["revenue_2024"]

    # Add financials if present
    if proff_data.get("financials"):
        merged["financials"] = proff_data["financials"]

    # Fill missing fields from Proff
    for key, value in proff_data.items():
        if not merged.get(key):
            merged[key] = value

    return merged
