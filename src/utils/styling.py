import streamlit as st
from src.config.plot_config import STYLE_CONFIG

def styled_header(text: str) -> None:
    """Render a consistently styled header."""
    st.markdown(
        f"<h2 style='{STYLE_CONFIG['header_style']}'>{text}</h2>",
        unsafe_allow_html=True
    )

def styled_subheader(text: str) -> None:
    """Render a consistently styled subheader."""
    st.markdown(
        f"<h3 style='{STYLE_CONFIG['subheader_style']}'>{text}</h3>",
        unsafe_allow_html=True
    )

def styled_description(text: str) -> None:
    """Render a consistently styled description."""
    st.markdown(
        f"<p style='{STYLE_CONFIG['description_style']}'>{text}</p>",
        unsafe_allow_html=True
    )

def styled_expander(text: str, expanded: bool = False):
    """Create a consistently styled expander."""
    return st.expander(
        text,
        expanded=expanded
    ) 