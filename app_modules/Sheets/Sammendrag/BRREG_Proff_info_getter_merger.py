from app_modules.Sheets.Sammendrag.BRREG_info_getter import fetch_company_by_org, format_company_data
from app_modules.Sheets.Sammendrag.Proff_info_getter import get_Proff_data
import streamlit as st

def merge_company_data(org_number: str) -> dict:
    st.write("MERGER STARTED")

    brreg = format_company_data(fetch_company_by_org(org_number)) or {}
    proff = get_Proff_data(org_number) or {}

    merged = brreg.copy()

    # Proff revenue goes to separate key
    if "revenue_2024" in proff:
        merged["revenue_2024_proff"] = proff["revenue_2024"]

    # Merge all financial years
    for key, value in proff.items():
        merged[key] = value

    st.write("FINAL MERGED:", merged)
    return merged
