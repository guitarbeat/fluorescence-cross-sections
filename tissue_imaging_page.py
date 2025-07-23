"""
Tissue Imaging Optimizer Page - Ready for embedding in other Streamlit projects.

Usage:
    from tissue_imaging_page import render_tissue_imaging_page
    
    # In your main app:
    render_tissue_imaging_page()
"""

import streamlit as st
from src.core import initialize_session_state
from src.components.dashboard_utils import add_dashboard_css, render_dashboard_metrics
from src.config import DEFAULT_TISSUE_PARAMS


def render_tissue_imaging_page():
    """Render the complete tissue imaging optimizer page."""
    
    # Add styling
    add_dashboard_css()
    
    # Initialize data
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 0.5rem 0; margin-bottom: 1rem;'>
        <h2 style='color: #0f4c81; margin: 0; font-size: 2rem;'>
            🔬 Deep Tissue Imaging Optimizer
        </h2>
        <p style='color: #666; font-size: 1rem; margin: 0.25rem 0;'>
            Advanced fluorescence analysis for tissue imaging
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics cards
    current_depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
    current_wavelength = st.session_state.global_params["normalization_wavelength"]
    current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    num_fluorophores = len(st.session_state.fluorophore_df) if "fluorophore_df" in st.session_state else 0
    
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
            render_plot_container("cross_sections", st.session_state.fluorophore_df)
        except Exception as e:
            st.error(f"Error: {e}")
    
    with col2:
        st.markdown("**Tissue Penetration**")
        try:
            from src.components.common import render_plot_container
            render_plot_container("tissue_penetration")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Mathematical Model with checkbox toggle to avoid nested expanders
    show_math_model = st.checkbox("🧮 Show Mathematical Model", value=False, help="Toggle detailed mathematical analysis")
    
    if show_math_model:
        st.markdown("#### Mathematical Tissue Model")
        try:
            from src.components.tissue_config import render_math_view
            render_math_view()
        except Exception as e:
            st.error(f"Error: {e}")
    elif st.session_state.get("show_math_model_info", True):
        st.info("👆 Check the box above to view the detailed mathematical tissue model with interactive parameters.")
        # Only show this info once per session
        st.session_state.show_math_model_info = False
    



# For standalone usage
if __name__ == "__main__":
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide"
    )
    render_tissue_imaging_page()