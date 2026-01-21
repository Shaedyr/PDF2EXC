from app_modules.Sheets.Sammendrag.BRREG_info_getter import fetch_company_by_org, format_company_data
from app_modules.Sheets.Sammendrag.Proff_info_getter import get_Proff_data


def merge_company_data(org_number: str) -> dict:
    import streamlit as st
    st.write("MERGER STARTED")

    """
    Fetches BRREG + Proff data for a company and merges them.
    - BRREG is primary source (identity, address, NACE, employees).
    - Proff always overrides revenue_2024.
    - Proff fills missing fields.
    - Proff adds financials.
    """

    BRREG_data = format_company_data(fetch_company_by_org(org_number)) or {}
    Proff_data = get_Proff_data(org_number) or {}

    merged = BRREG_data.copy()

    # Always prefer Proff revenue
    if Proff_data.get("revenue_2024"):
        merged["revenue_2024"] = Proff_data["revenue_2024"]

    # Add financials if present
    if Proff_data.get("financials"):
        merged["financials"] = Proff_data["financials"]

    # Fill missing fields from Proff
    for key, value in Proff_data.items():
        if not merged.get(key):
            merged[key] = value

    print("MERGED KEYS:", merged.keys())

    return merged
