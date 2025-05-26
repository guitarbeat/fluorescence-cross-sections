"""Fluorophore Library Page"""
import streamlit as st
from src.api.search_form import render_search_panel
from src.components.fluorophore_viewer import render_fluorophore_viewer
from src.utils.data_loader import load_cross_section_data

# Main fluorophore library page
st.header("📚 Fluorophore Discovery")
st.caption("Browse, search, and manage your fluorophore database")

# Data Source Tabs
lib_tab1, lib_tab2 = st.tabs([
    "📊 Cross Section Data",
    "🔍 FPbase Search"
])

with lib_tab1:
    st.info("""
        Browse the complete library of two-photon cross section data.
        Select a fluorophore to view its detailed data and add it to your main table.
    """)
    cross_sections = load_cross_section_data()
    render_fluorophore_viewer(cross_sections, key_prefix="main")

with lib_tab2:
    st.info("""
        Search the FPbase database for additional fluorophores.
        Found proteins can be added to your main fluorophore table.
    """)
    render_search_panel(key_prefix="lib_")
