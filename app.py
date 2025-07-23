"""Entry point for the Deep Tissue Imaging Optimizer."""
import streamlit as st

from src.core import initialize_session_state


def main():
    """Main application entry point."""
    # Page setup
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    initialize_session_state()
    
    # Main header
    st.header("🔬 Deep Tissue Imaging Optimizer")
    
    # Essential Configuration - Compact horizontal layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        wavelength_range = st.select_slider(
            "🌊 Wavelength Range",
            options=range(700, 1701, 50),  # Extended to 1700 to include current session state
            value=st.session_state.global_params["wavelength_range"],
            help="Analysis wavelength range"
        )
        st.session_state.global_params["wavelength_range"] = wavelength_range
    
    with col2:
        norm_wavelength = st.number_input(
            "🎯 Normalization λ",
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
            "📏 Tissue Depth",
            min_value=0.1,
            max_value=5.0,
            value=st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"]),
            step=0.1,
            help="Tissue penetration depth"
        )
        st.session_state.tissue_params["depth"] = depth
    
    with col4:
        # Convert session state value to integer if it's a float
        current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
        if isinstance(current_water, float):
            current_water = int(current_water * 100)
        
        water_content = st.select_slider(
            "💧 Water Content",
            options=[40, 50, 60, 70, 75, 80, 90],
            value=current_water,
            help="Tissue water content percentage"
        )
        # Store as float for consistency with mathematical model
        st.session_state.tissue_params["water_content"] = water_content / 100
    
    # Laser configuration in sidebar
    with st.sidebar:
        st.header("⚙️ Laser Configuration")
        from src.components.laser_manager import render_laser_manager
        render_laser_manager()
    
    # Main content grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Cross-Sections Analysis")
        try:
            from src.components.common import render_plot_container
            render_plot_container("cross_sections", st.session_state.fluorophore_df)
        except Exception as e:
            st.error(f"Error loading cross-section analysis: {e}")
    
    with col2:
        st.subheader("🩸 Tissue Penetration Analysis")
        try:
            from src.components.common import render_plot_container
            render_plot_container("tissue_penetration")
        except Exception as e:
            st.error(f"Error loading tissue penetration analysis: {e}")
    
    # Mathematical model section
    st.subheader("🧮 Mathematical Tissue Model")
    try:
        from src.components.tissue_config import render_math_view
        render_math_view()
    except Exception as e:
        st.error(f"Error loading mathematical model: {e}")
    
    # Fluorophore library with tabs
    st.subheader("🔬 Fluorophore Library")
    
    tab1, tab2 = st.tabs(["Cross Section Data", "FPbase Search"])
    
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
    
    # Footer
    st.markdown("---")
    st.markdown("*Deep Tissue Imaging Optimizer - Advanced fluorescence analysis for tissue imaging*")


if __name__ == "__main__":
    main()