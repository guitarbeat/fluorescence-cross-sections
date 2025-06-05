"""Entry point for the Deep Tissue Imaging Optimizer."""

import streamlit as st

from src.state.session_state import initialize_session_state

st.set_page_config(
    page_title="Deep Tissue Imaging Optimizer",
    page_icon="src/assets/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_session_state()

PAGES = {
    "Configuration": [
        st.Page("pages/1_laser_config.py", title="Laser Configuration", icon="🎯", default=True),
        st.Page("pages/2_wavelength_settings.py", title="Wavelength Settings", icon="📏"),
        st.Page("pages/3_tissue_parameters.py", title="Tissue Parameters", icon="🧬"),
    ],
    "Analysis": [
        st.Page("pages/4_cross_sections.py", title="Cross-sections", icon="📈"),
        st.Page("pages/5_tissue_penetration.py", title="Tissue Penetration", icon="🩻"),
    ],
    "Library": [
        st.Page("pages/6_fluorophore_library.py", title="Fluorophore Discovery", icon="📚"),
    ],
}

st.navigation(PAGES)
