import streamlit as st
import app_modules.input as input_module

# Configure layout (wide, no sidebar)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stSidebarNav"] {display: none;}
        [data-testid="stSidebarContent"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# Imports
from app_modules import main_page
from app_modules.Sheets.Sammendrag import Brreg_info_getter
from app_modules import pdf_parser
from app_modules.Sheets.Sammendrag import Summary_getter
from app_modules import excel_filler
from app_modules import template_loader
from app_modules import download
from app_modules.Sheets.Sammendrag import Proff_info_getter
from app_modules.Sheets.Sammendrag import BRREG_Proff_info_getter_merger


def main():
    # Run one default page directly (no sidebar navigation)
    main_page.run()


if __name__ == "__main__":
    main()
