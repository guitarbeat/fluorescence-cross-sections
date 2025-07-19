import streamlit as st

from src.pages.common import render_footer, render_plot_container
from src.state.session_state import initialize_session_state

initialize_session_state()

st.header(
    "Cross-sections Overview",
    help="Compare two-photon cross-sections of different fluorophores",
)

st.caption(
    "View and compare two-photon cross-sections of different fluorophores"
)

render_plot_container("cross_sections", st.session_state.fluorophore_df)

render_footer()
