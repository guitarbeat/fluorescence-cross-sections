"""Entry point for the Deep Tissue Imaging Optimizer."""
import streamlit as st
import numpy as np

from src.core import initialize_session_state
from src.components.dashboard_utils import (
    create_metric_card, 
    create_section_header, 
    render_dashboard_metrics,
    create_collapsible_section,
    add_dashboard_css
)


def render_dashboard_header():
    """Render the dashboard header with title and key metrics."""
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


def render_metrics_cards():
    """Render key metrics cards at the top of the dashboard."""
    from src.config import DEFAULT_TISSUE_PARAMS
    
    # Calculate key metrics
    current_depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
    current_wavelength = st.session_state.global_params["normalization_wavelength"]
    current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    num_fluorophores = len(st.session_state.fluorophore_df) if "fluorophore_df" in st.session_state else 0
    
    # More compact metrics - only show the most important ones
    metrics = {
        "depth": {
            "title": "Depth",
            "value": f"{current_depth:.1f}mm"
        },
        "wavelength": {
            "title": "Wavelength", 
            "value": f"{current_wavelength}nm"
        },
        "water": {
            "title": "Water",
            "value": f"{current_water*100:.0f}%"
        },
        "fluorophores": {
            "title": "Fluorophores",
            "value": str(num_fluorophores)
        }
    }
    
    render_dashboard_metrics(metrics)


def render_control_panel():
    """Render the main control panel with parameters."""
    st.markdown("#### ⚙️ Parameters")
    
    # Compact parameter layout in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        wavelength_range = st.select_slider(
            "Wavelength Range",
            options=range(700, 1701, 50),
            value=st.session_state.global_params["wavelength_range"],
            help="Analysis wavelength range (nm)"
        )
        st.session_state.global_params["wavelength_range"] = wavelength_range
    
    with col2:
        norm_wavelength = st.number_input(
            "Norm. λ (nm)",
            value=st.session_state.global_params["normalization_wavelength"],
            min_value=700,
            max_value=1600,
            step=10,
            help="Normalization wavelength"
        )
        st.session_state.global_params["normalization_wavelength"] = norm_wavelength
    
    with col3:
        from src.config import DEFAULT_TISSUE_PARAMS
        depth = st.slider(
            "Depth (mm)",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"]),
            step=0.1,
            help="Tissue penetration depth"
        )
        st.session_state.tissue_params["depth"] = depth
    
    with col4:
        current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
        if isinstance(current_water, float):
            current_water = int(current_water * 100)
        
        water_content = st.select_slider(
            "Water (%)",
            options=[40, 50, 60, 70, 75, 80, 90],
            value=current_water,
            help="Tissue water content"
        )
        st.session_state.tissue_params["water_content"] = water_content / 100
    
    # Laser configuration in an expander to save space
    with st.expander("🔬 Laser Configuration", expanded=False):
        try:
            from src.components.laser_manager import render_laser_manager
            render_laser_manager()
        except Exception as e:
            st.error(f"Error loading laser configuration: {e}")


def render_analysis_dashboard():
    """Render the main analysis dashboard with plots."""
    st.markdown("#### 📊 Analysis")
    
    # Main analysis plots side by side
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


def render_mathematical_model():
    """Render the mathematical model section."""
    show_math_model = st.checkbox("🧮 Show Mathematical Model", value=False, help="Toggle detailed mathematical analysis")
    
    if show_math_model:
        st.markdown("#### Mathematical Tissue Model")
        try:
            from src.components.tissue_config import render_math_view
            render_math_view()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("👆 Check the box above to view the detailed mathematical tissue model with interactive parameters.")


def render_fluorophore_library():
    """Render the fluorophore library section."""
    with st.expander("🔬 Fluorophore Library", expanded=False):
        tab1, tab2 = st.tabs(["Cross Section Data", "FPbase Search"])
        
        with tab1:
            try:
                from src.components.fluorophore_viewer import render_fluorophore_viewer
                from src.utils.data_loader import load_cross_section_data
                cross_sections = load_cross_section_data()
                render_fluorophore_viewer(cross_sections, key_prefix="main")
            except Exception as e:
                st.error(f"Error: {e}")
        
        with tab2:
            try:
                from src.api.search_form import render_search_panel
                render_search_panel(key_prefix="lib_")
            except Exception as e:
                st.error(f"Error: {e}")


def main():
    """Main application entry point."""
    # Page setup - removed sidebar configuration since it will be embedded
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Use the standalone page renderer
    from tissue_imaging_page import render_tissue_imaging_page
    render_tissue_imaging_page()


if __name__ == "__main__":
    main()