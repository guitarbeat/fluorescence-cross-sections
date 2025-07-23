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
    <div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
        <h1 style='color: #0f4c81; margin: 0; font-size: 2.5rem;'>
            🔬 Deep Tissue Imaging Optimizer
        </h1>
        <p style='color: #666; font-size: 1.1rem; margin: 0.5rem 0;'>
            Advanced fluorescence analysis for tissue imaging applications
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
    
    # Calculate wavelength range span
    wavelength_range = st.session_state.global_params["wavelength_range"]
    if isinstance(wavelength_range, (tuple, list)) and len(wavelength_range) == 2:
        range_span = wavelength_range[1] - wavelength_range[0]
    else:
        range_span = wavelength_range if isinstance(wavelength_range, (int, float)) else 1000
    
    metrics = {
        "depth": {
            "title": "Tissue Depth",
            "value": f"{current_depth:.1f} mm",
            "subtitle": "Penetration depth"
        },
        "wavelength": {
            "title": "Norm. Wavelength", 
            "value": f"{current_wavelength} nm",
            "subtitle": "Reference point"
        },
        "water": {
            "title": "Water Content",
            "value": f"{current_water*100:.0f}%",
            "subtitle": "Tissue composition"
        },
        "fluorophores": {
            "title": "Fluorophores",
            "value": str(num_fluorophores),
            "subtitle": "Active markers"
        },
        "range": {
            "title": "Analysis Range",
            "value": f"{range_span} nm",
            "subtitle": "Spectral window"
        }
    }
    
    render_dashboard_metrics(metrics)


def render_control_panel():
    """Render the main control panel with parameters."""
    create_section_header("⚙️ Control Panel", "Configure analysis parameters and laser settings")
    
    with st.container():
        # Create tabs for different parameter groups
        param_tab1, param_tab2, param_tab3 = st.tabs(["🌊 Wavelength", "🧬 Tissue", "🔬 Lasers"])
        
        with param_tab1:
            col1, col2 = st.columns(2)
            with col1:
                wavelength_range = st.select_slider(
                    "Analysis Wavelength Range (nm)",
                    options=range(700, 1701, 50),
                    value=st.session_state.global_params["wavelength_range"],
                    help="Wavelength range for analysis"
                )
                st.session_state.global_params["wavelength_range"] = wavelength_range
            
            with col2:
                norm_wavelength = st.number_input(
                    "Normalization Wavelength (nm)",
                    value=st.session_state.global_params["normalization_wavelength"],
                    min_value=700,
                    max_value=1600,
                    step=10,
                    help="Reference wavelength for normalization"
                )
                st.session_state.global_params["normalization_wavelength"] = norm_wavelength
        
        with param_tab2:
            from src.config import DEFAULT_TISSUE_PARAMS
            col1, col2 = st.columns(2)
            
            with col1:
                depth = st.slider(
                    "Tissue Penetration Depth (mm)",
                    min_value=0.1,
                    max_value=5.0,
                    value=st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"]),
                    step=0.1,
                    help="Depth of tissue penetration"
                )
                st.session_state.tissue_params["depth"] = depth
            
            with col2:
                current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
                if isinstance(current_water, float):
                    current_water = int(current_water * 100)
                
                water_content = st.select_slider(
                    "Water Content (%)",
                    options=[40, 50, 60, 70, 75, 80, 90],
                    value=current_water,
                    help="Tissue water content percentage"
                )
                st.session_state.tissue_params["water_content"] = water_content / 100
        
        with param_tab3:
            try:
                from src.components.laser_manager import render_laser_manager
                render_laser_manager()
            except Exception as e:
                st.error(f"Error loading laser configuration: {e}")


def render_analysis_dashboard():
    """Render the main analysis dashboard with plots."""
    create_section_header("📊 Analysis Dashboard", "Real-time visualization of tissue penetration and cross-sections")
    
    # Main analysis plots in a 2x2 grid
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        with st.container():
            st.markdown("#### 📈 Cross-Sections Analysis")
            try:
                from src.components.common import render_plot_container
                render_plot_container("cross_sections", st.session_state.fluorophore_df)
            except Exception as e:
                st.error(f"Error loading cross-section analysis: {e}")
    
    with row1_col2:
        with st.container():
            st.markdown("#### 🩸 Tissue Penetration Analysis")
            try:
                from src.components.common import render_plot_container
                render_plot_container("tissue_penetration")
            except Exception as e:
                st.error(f"Error loading tissue penetration analysis: {e}")


def render_mathematical_model():
    """Render the mathematical model section."""
    create_section_header("🧮 Mathematical Tissue Model", "Detailed mathematical analysis with interactive controls")
    
    def render_math_content():
        try:
            from src.components.tissue_config import render_math_view
            render_math_view()
        except Exception as e:
            st.error(f"Error loading mathematical model: {e}")
    
    create_collapsible_section(
        "Mathematical Tissue Model",
        render_math_content,
        default_expanded=False,
        help_text="Toggle detailed mathematical analysis with interactive parameters"
    )


def render_fluorophore_library():
    """Render the fluorophore library section."""
    create_section_header("🔬 Fluorophore Library", "Browse and search fluorophore databases")
    
    tab1, tab2 = st.tabs(["📚 Cross Section Data", "🔍 FPbase Search"])
    
    with tab1:
        try:
            from src.components.fluorophore_viewer import render_fluorophore_viewer
            from src.utils.data_loader import load_cross_section_data
            cross_sections = load_cross_section_data()
            render_fluorophore_viewer(cross_sections, key_prefix="main")
        except Exception as e:
            st.error(f"Error loading cross-section data: {e}")
    
    with tab2:
        try:
            from src.api.search_form import render_search_panel
            render_search_panel(key_prefix="lib_")
        except Exception as e:
            st.error(f"Error loading FPbase search: {e}")


def main():
    """Main application entry point."""
    # Page setup with custom theme
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Add dashboard CSS styling
    add_dashboard_css()
    
    initialize_session_state()
    
    # Sidebar with quick actions
    with st.sidebar:
        st.markdown("### 🚀 Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("📊 Export Results", use_container_width=True):
            st.info("Export functionality coming soon!")
        
        st.markdown("---")
        st.markdown("### 📈 System Status")
        
        # System status indicators
        from src.config import DEFAULT_TISSUE_PARAMS
        num_fluorophores = len(st.session_state.fluorophore_df) if "fluorophore_df" in st.session_state else 0
        
        status_items = [
            ("Data Loaded", "✅" if num_fluorophores > 0 else "⚠️"),
            ("Parameters Set", "✅"),
            ("Analysis Ready", "✅" if num_fluorophores > 0 else "⚠️"),
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}:** {status}")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        **Version:** 2.0.0  
        **Last Updated:** 2025-07-23  
        **Status:** 🟢 Active
        
        **Features:**
        - Real-time analysis
        - Interactive parameters
        - Multi-source data
        - Export capabilities
        """)
    
    # Dashboard layout
    render_dashboard_header()
    
    # Quick info banner
    st.info("💡 **Quick Start:** Adjust parameters in the Control Panel below, then view real-time analysis in the Dashboard section.")
    
    render_metrics_cards()
    
    st.markdown("---")
    
    # Control panel
    render_control_panel()
    
    st.markdown("---")
    
    # Main analysis dashboard
    render_analysis_dashboard()
    
    st.markdown("---")
    
    # Mathematical model (collapsible)
    render_mathematical_model()
    
    st.markdown("---")
    
    # Fluorophore library
    render_fluorophore_library()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p><strong>Deep Tissue Imaging Optimizer</strong> | Advanced fluorescence analysis for tissue imaging</p>
        <p style='font-size: 0.9rem;'>Developed with ❤️ for the scientific community</p>
    </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()