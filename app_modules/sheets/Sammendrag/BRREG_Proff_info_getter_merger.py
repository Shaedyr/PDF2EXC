from app_modules.sheets.sammendrag.BRREG_info_getter import fetch_company_by_org, format_company_data
from app_modules.sheets.sammendrag.Proff_info_getter import get_Proff_data
import streamlit as st


def merge_company_data(org_number: str) -> dict:
    st.write("MERGER STARTED")

    brreg = format_company_data(fetch_company_by_org(org_number)) or {}
    proff = get_Proff_data(org_number) or {}

    merged = brreg.copy()

    if "revenue_2024" in proff:
        merged["revenue_2024_proff"] = proff["revenue_2024"]

    for key, value in proff.items():
        merged[key] = value

    st.write("FINAL MERGED:", merged)
    return merged
