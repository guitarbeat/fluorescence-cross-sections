"""Plot utility functions for consistent chart rendering."""
import streamlit as st


def render_simple_plotly_chart(fig) -> None:
    """Render a Plotly chart with standard Streamlit settings (no settings popover)."""
    # * Renders a Plotly chart with consistent settings
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme="streamlit",
        config={"displayModeBar": True, "responsive": True},
    )
