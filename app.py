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

# * Sidebar navigation
st.sidebar.title("Navigation")

# * Get current page from URL parameters or default to home
page = st.query_params.get("page", "home")

# Configuration section
st.sidebar.header("Configuration")
if st.sidebar.button("🎯 Laser Configuration"):
    st.query_params["page"] = "laser_config"
    st.rerun()
if st.sidebar.button("📏 Wavelength Settings"):
    st.query_params["page"] = "wavelength_settings"
    st.rerun()
if st.sidebar.button("🧬 Tissue Parameters"):
    st.query_params["page"] = "tissue_parameters"
    st.rerun()

# Analysis section
st.sidebar.header("Analysis")
if st.sidebar.button("📈 Cross-sections"):
    st.query_params["page"] = "cross_sections"
    st.rerun()
if st.sidebar.button("🩻 Tissue Penetration"):
    st.query_params["page"] = "tissue_penetration"
    st.rerun()

# Library section
st.sidebar.header("Library")
if st.sidebar.button("📚 Fluorophore Discovery"):
    st.query_params["page"] = "fluorophore_library"
    st.rerun()

# * Main content area based on selected page
if page == "home":
    st.title("Deep Tissue Imaging Optimizer")
    st.write("Welcome to the Deep Tissue Imaging Optimizer!")
    
    st.header("Getting Started")
    st.write("""
    This application helps optimize deep tissue imaging by analyzing:
    - Laser configurations for optimal penetration
    - Wavelength settings for specific fluorophores
    - Tissue parameters and their effects
    - Cross-sections and absorption characteristics
    - Tissue penetration depth calculations
    - Fluorophore discovery and selection
    """)
    
    st.info("Use the sidebar navigation to explore different sections of the application.")

elif page == "laser_config":
    st.header("🎯 Laser Configuration")
    st.write("Configure and manage laser settings for visualization")
    # * Import and render laser manager component
    try:
        from src.components.laser_manager import render_laser_manager
        render_laser_manager()
    except Exception as e:
        st.error(f"Error loading laser configuration: {e}")
        st.info("Please check the component implementation.")

elif page == "wavelength_settings":
    st.header("📏 Wavelength Settings")
    st.write("Configure wavelength settings for optimal imaging")
    # * Import and render wavelength settings
    try:
        # * Add wavelength settings content here
        st.info("Wavelength settings functionality coming soon...")
    except Exception as e:
        st.error(f"Error loading wavelength settings: {e}")

elif page == "tissue_parameters":
    st.header("🧬 Tissue Parameters")
    st.write("Configure tissue parameters for accurate modeling")
    # * Import and render tissue parameters
    try:
        # * Add tissue parameters content here
        st.info("Tissue parameters functionality coming soon...")
    except Exception as e:
        st.error(f"Error loading tissue parameters: {e}")

elif page == "cross_sections":
    st.header("📈 Cross-sections")
    st.write("Analyze cross-sections and absorption characteristics")
    # * Import and render cross-sections
    try:
        # * Add cross-sections content here
        st.info("Cross-sections functionality coming soon...")
    except Exception as e:
        st.error(f"Error loading cross-sections: {e}")

elif page == "tissue_penetration":
    st.header("🩻 Tissue Penetration")
    st.write("Calculate and visualize tissue penetration depth")
    # * Import and render tissue penetration
    try:
        # * Add tissue penetration content here
        st.info("Tissue penetration functionality coming soon...")
    except Exception as e:
        st.error(f"Error loading tissue penetration: {e}")

elif page == "fluorophore_library":
    st.header("📚 Fluorophore Discovery")
    st.write("Discover and analyze fluorophores for imaging")
    # * Import and render fluorophore library
    try:
        # * Add fluorophore library content here
        st.info("Fluorophore library functionality coming soon...")
    except Exception as e:
        st.error(f"Error loading fluorophore library: {e}")

else:
    st.error(f"Unknown page: {page}")
    st.query_params["page"] = "home"
    st.rerun()