import streamlit as st

from src.pages.common import render_footer, render_plot_container
from src.state.session_state import initialize_session_state

initialize_session_state()

st.header(
    "Tissue Penetration Analysis",
    help="Analyze how light penetrates through tissue",
)

st.caption("Analyze tissue penetration characteristics and parameters")

render_plot_container("tissue_penetration")

render_footer()
