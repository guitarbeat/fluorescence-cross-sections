"""Entry point for the Deep Tissue Imaging Optimizer."""
import streamlit as st

from src.state.session_state import initialize_session_state

st.set_page_config(
    page_title="Deep Tissue Imaging Optimizer",
    page_icon="🔬",  # Use emoji instead of file path
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_session_state()

# * Main content - Everything on one page to minimize clicks
st.header("Deep Tissue Imaging Optimizer")

# * Essential Configuration - Always visible, no clicks needed
col1, col2 = st.columns(2)

with col1:
    st.subheader("Wavelength Settings")
    wavelength_range = st.slider(
        "Analysis Range (nm)",
        min_value=700,
        max_value=2400,
        value=st.session_state.global_params["wavelength_range"],
        step=10,
    )
    st.session_state.global_params["wavelength_range"] = wavelength_range
    
    norm_wavelength = st.number_input(
        "Normalization λ (nm)",
        min_value=800,
        max_value=2400,
        value=st.session_state.global_params["normalization_wavelength"],
        step=10,
    )
    st.session_state.global_params["normalization_wavelength"] = norm_wavelength

with col2:
    st.subheader("Tissue Parameters")
    from src.config.constants import TISSUE_DEPTH_SLIDER_CONFIG
    from src.config.tissue_config import DEFAULT_TISSUE_PARAMS
    
    depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
    new_depth = st.slider(
        "Tissue Depth (mm)",
        value=depth,
        key="tissue_depth_main",
        **TISSUE_DEPTH_SLIDER_CONFIG,
    )
    if new_depth != depth:
        st.session_state.tissue_params["depth"] = new_depth
    
    water_content = st.select_slider(
        "Water Content",
        options=[i / 100 for i in range(0, 105, 5)],
        value=st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"]),
    )
    st.session_state.tissue_params["water_content"] = water_content

# * Collapsible sections for detailed views
with st.expander("Laser Configuration", expanded=False):
    try:
        from src.components.laser_manager import render_laser_manager
        render_laser_manager()
    except Exception as e:
        st.error(f"Error loading laser configuration: {e}")

with st.expander("Cross-sections Analysis", expanded=False):
    try:
        from src.pages.common import render_plot_container
        render_plot_container("cross_sections", st.session_state.fluorophore_df)
    except Exception as e:
        st.error(f"Error loading cross-sections: {e}")

with st.expander("Tissue Penetration Analysis", expanded=False):
    try:
        from src.pages.common import render_plot_container
        render_plot_container("tissue_penetration")
    except Exception as e:
        st.error(f"Error loading tissue penetration: {e}")
        st.info("Please check the tissue penetration component implementation.")

# * Mathematical Tissue Analysis - Detailed controls and plots
st.subheader("Tissue Penetration Mathematical Model")
st.write("Detailed mathematical analysis of tissue penetration with interactive controls")

try:
    from src.config.tissue_config import render_math_view
    render_math_view()
except Exception as e:
    st.error(f"Error loading mathematical tissue analysis: {e}")
    st.info("Please check the tissue configuration component implementation.")

# * Fluorophore Discovery - Using tabs instead of expander to avoid nesting
st.subheader("Fluorophore Discovery")
st.write("Browse, search, and manage your fluorophore database")

try:
    from src.api.search_form import render_search_panel
    from src.components.fluorophore_viewer import render_fluorophore_viewer
    from src.utils.data_loader import load_cross_section_data
    
    lib_tab1, lib_tab2 = st.tabs([
        "Cross Section Data",
        "FPbase Search",
    ])

    with lib_tab1:
        st.info(
            """Browse the complete library of two-photon cross section data.\nSelect a fluorophore to view its detailed data and add it to your main table."""
        )
        cross_sections = load_cross_section_data()
        render_fluorophore_viewer(cross_sections, key_prefix="main")

    with lib_tab2:
        st.info(
            """Search the FPbase database for additional fluorophores.\nFound proteins can be added to your main fluorophore table."""
        )
        render_search_panel(key_prefix="lib_")
except Exception as e:
    st.error(f"Error loading fluorophore library: {e}")

# * Add footer
try:
    from src.pages.common import render_footer
    render_footer()
except Exception as e:
    st.error(f"Error loading footer: {e}")