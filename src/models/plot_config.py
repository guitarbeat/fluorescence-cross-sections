"""Configuration for plot styling and themes."""

from typing import Any, Dict

# Theme configurations
PLOT_THEMES = {
    "light": {
        "grid_color": "rgba(0, 0, 0, 0.1)",
        "text_color": "black",
        "bg_color": "rgba(255, 255, 255, 0)",
        "plot_template": "plotly_white",
        "axis_line_color": "black",
    },
    "dark": {
        "grid_color": "rgba(255, 255, 255, 0.1)",
        "text_color": "white",
        "bg_color": "rgba(0, 0, 0, 0)",
        "plot_template": "plotly_dark",
        "axis_line_color": "white",
    },
}


def get_theme_colors() -> Dict[str, Any]:
    """Get current theme colors based on Streamlit's theme."""
    import streamlit as st

    theme = "dark" if st.get_option("theme.base") == "dark" else "light"
    return PLOT_THEMES[theme]
