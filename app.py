import streamlit as st
import app_modules.input as input_module
import app_modules.main_page as main_page

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

main_page.run()
