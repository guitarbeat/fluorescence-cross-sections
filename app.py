"""Entry point for the Deep Tissue Imaging Optimizer."""
from src.config import DEFAULT_TISSUE_PARAMS
from src.components.dashboard_utils import add_dashboard_css, render_dashboard_metrics
from src.core import initialize_session_state
import streamlit as st


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    # Add styling
    add_dashboard_css()

    # Initialize data
    initialize_session_state()

    # Metrics cards
    current_depth = st.session_state.tissue_params.get(
        "depth", DEFAULT_TISSUE_PARAMS["depth"])
    current_wavelength = st.session_state.global_params["normalization_wavelength"]
    current_water = st.session_state.tissue_params.get(
        "water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    num_fluorophores = len(
        st.session_state.fluorophore_df) if "fluorophore_df" in st.session_state else 0

    metrics = {
        "depth": {"title": "Depth", "value": f"{current_depth:.1f}mm"},
        "wavelength": {"title": "Wavelength", "value": f"{current_wavelength}nm"},
        "water": {"title": "Water", "value": f"{current_water*100:.0f}%"},
        "fluorophores": {"title": "Fluorophores", "value": str(num_fluorophores)},
        "laser": {"title": "Laser", "value": "Config"}
    }
    render_dashboard_metrics(metrics)

    # Analysis plots
    st.markdown("#### 📊 Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Cross-Sections**")
        try:
            from src.components.common import render_plot_container
            render_plot_container(
                "cross_sections", st.session_state.fluorophore_df)
        except Exception as e:
            st.error(f"Error: {e}")

    with col2:
        st.markdown("**Tissue Penetration**")
        try:
            from src.components.common import render_plot_container
            render_plot_container("tissue_penetration")
        except Exception as e:
            st.error(f"Error: {e}")

    try:
        from src.components.tissue_config import render_math_view
        render_math_view()
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
