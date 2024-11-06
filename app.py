import logging
import os
import sys
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI
from src.api.search_form import render_search_panel
from src.components.laser_manager import render_laser_manager
from src.components.results_table import render_results_panel
from src.models.tissue_model import calculate_tissue_parameters
from src.plots.cross_section_plot import (create_cross_section_plot,
                                          get_marker_settings,
                                          marker_settings_ui)
from src.plots.tissue_plot import create_tissue_plot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add 'src' directory to Python path
try:
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if src_path not in sys.path:
        sys.path.append(src_path)
except Exception as e:
    logger.error(f"Error setting up Python path: {e}")
    st.error("Error initializing application. Please check logs.")


def initialize_session_state() -> None:
    """Initialize or reset session state variables with parameters from src."""
    session_state = st.session_state

    # Initialize API client
    session_state.setdefault("fpbase_client", FPbaseAPI())

    # Load existing fluorophores from CSV
    try:
        fluorophore_df = pd.read_csv("data/fluorophores.csv")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        fluorophore_df = pd.DataFrame(
            columns=[
                "Name",
                "Wavelength",
                "Cross_Section",
                "Reference",
                "Ex_Max",
                "Em_Max",
                "QY",
                "EC",
                "pKa",
                "Brightness",
            ]
        )

    # Initialize dataframes
    session_state.setdefault("fluorophore_df", fluorophore_df)
    session_state.setdefault(
        "search_results", pd.DataFrame(columns=fluorophore_df.columns)
    )

    # Initialize global parameters with defaults
    session_state.setdefault(
        "global_params",
        {
            "wavelength_range": (700, 2000),
            "depth": 1.0,
            "normalization_wavelength": 1300,
            "absorption_threshold": 50,
            "plot_theme": "dark" if st.get_option("theme.base") == "dark" else "light",
        },
    )

    # Initialize tissue parameters
    session_state.setdefault(
        "tissue_params",
        {
            "water_content": 0.75,
            "g": 0.9,
            "a": 1.1,
            "b": 1.37,
            "mu_a_base": 1.37,
        },
    )

    # Initialize plot settings
    session_state.setdefault(
        "plot_settings",
        {
            "show_lasers": True,
            "show_grid": True,
            "show_legend": True,
        },
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_tissue_data(wavelengths, depth, norm_wavelength):
    """Cache tissue calculations to improve performance."""
    return calculate_tissue_parameters(
        wavelengths=wavelengths, depth=depth, normalization_wavelength=norm_wavelength
    )


def render_plot_container(plot_type: str, df: Optional[pd.DataFrame] = None) -> None:
    """Render plot containers with consistent error handling."""
    try:
        # Get parameters from session state
        global_params = st.session_state.global_params
        depth = global_params["depth"]
        norm_wavelength = global_params["normalization_wavelength"]
        wavelength_range = global_params["wavelength_range"]

        if plot_type == "cross_sections":
            # Create two columns: one for controls/data, one for plot
            col1, col2 = st.columns([1, 2])

            with col1:
                render_results_panel()
                st.divider()
                marker_settings_ui()

            with col2:
                if df is not None and not df.empty:
                    markers_dict = get_marker_settings()
                    fig = create_cross_section_plot(
                        df,
                        markers_dict=markers_dict,
                        normalization_wavelength=norm_wavelength,
                        depth=depth,
                        wavelength_range=wavelength_range,
                    )
                    st.plotly_chart(fig, use_container_width=True, theme=None)
                else:
                    st.info("No data to display - try searching for fluorophores.")

        elif plot_type == "tissue_penetration":
            col1, col2 = st.columns([1, 2])

            with col1:
                from src.plots.tissue_view import \
                    render_tissue_penetration_view

                render_tissue_penetration_view(controls_only=True)

            with col2:
                # Calculate tissue parameters with caching
                wavelengths = np.linspace(
                    wavelength_range[0], wavelength_range[1], 1000
                )
                tissue_data = get_cached_tissue_data(
                    wavelengths, depth, norm_wavelength
                )

                fig = create_tissue_plot(
                    wavelengths=wavelengths,
                    tissue_data=tissue_data,
                    normalization_wavelength=norm_wavelength,
                    depth=depth,
                )
                st.plotly_chart(fig, use_container_width=True, theme=None)

    except Exception as e:
        logger.error(f"Error rendering {plot_type} plot: {e}")
        st.error(f"Error creating {plot_type} plot: {str(e)}")


def main() -> None:
    """Main application function."""
    try:
        # Page configuration
        st.set_page_config(
            page_title="Deep Tissue Imaging Optimizer",
            page_icon="🔬",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Initialize session state
        initialize_session_state()

        # Sidebar with better organization
        with st.sidebar:
            st.title("🔬 Deep Tissue Optimizer")

            # Search and Database Section
            render_search_panel()

            st.divider()

            # Plot Settings Section
            with st.expander("📊 Plot Settings", expanded=False):
                # Theme Controls
                st.markdown("#### Theme")
                plot_theme = st.selectbox(
                    "Color Theme",
                    options=["Auto", "Light", "Dark"],
                    help="Select plot color theme. Auto matches Streamlit's theme.",
                )
                if plot_theme != "Auto":
                    st.session_state.global_params["plot_theme"] = plot_theme.lower()
                else:
                    st.session_state.global_params["plot_theme"] = (
                        "dark" if st.get_option("theme.base") == "dark" else "light"
                    )

                # Plot Display Options
                st.markdown("#### Display Options")
                st.session_state.plot_settings["show_grid"] = st.checkbox(
                    "Show Grid",
                    value=st.session_state.plot_settings["show_grid"],
                    help="Toggle grid lines on plots",
                )
                st.session_state.plot_settings["show_legend"] = st.checkbox(
                    "Show Legend",
                    value=st.session_state.plot_settings["show_legend"],
                    help="Toggle plot legends",
                )

            st.divider()

            # Analysis Parameters Section
            with st.expander("⚙️ Analysis Parameters", expanded=True):
                st.markdown("#### Wavelength Settings")
                # Wavelength Range
                wavelength_range = st.slider(
                    "Analysis Range (nm)",
                    min_value=700,
                    max_value=2400,
                    value=st.session_state.global_params["wavelength_range"],
                    step=10,
                    help="Global wavelength range for all plots and analysis",
                )
                st.session_state.global_params["wavelength_range"] = wavelength_range

                # Normalization Wavelength
                norm_wavelength = st.number_input(
                    "Normalization λ (nm)",
                    min_value=800,
                    max_value=2400,
                    value=st.session_state.global_params["normalization_wavelength"],
                    step=10,
                    help="Wavelength at which to normalize the photon fraction",
                )
                st.session_state.global_params["normalization_wavelength"] = (
                    norm_wavelength
                )

                st.markdown("#### Tissue Parameters")
                # Imaging Depth
                depth = st.number_input(
                    "Tissue Depth (mm)",
                    min_value=0.1,
                    max_value=2.0,
                    value=st.session_state.global_params["depth"],
                    step=0.1,
                    help="Global imaging depth for analysis",
                )
                st.session_state.global_params["depth"] = depth

                # Absorption Threshold
                absorption_threshold = st.slider(
                    "Absorption Threshold (%)",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.global_params["absorption_threshold"],
                    help="Threshold for absorption shading",
                )
                st.session_state.global_params["absorption_threshold"] = (
                    absorption_threshold
                )

            st.divider()

            # Laser Management Section
            render_laser_manager()

            # Footer with info
            st.markdown("---")
            st.markdown(
                """
                <div style='text-align: center; color: gray; font-size: 0.8em;'>
                Developed by Aaron Woods<br>
                Data from <a href="https://www.fpbase.org">FPbase</a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Main content area
        st.title("Deep Tissue Imaging Optimizer")

        # View mode selector
        st.markdown("### Plot Display")
        tab1, tab2, tab3 = st.tabs(
            ["Cross-sections Overview", "Tissue Penetration", "Non-Degenerate Analysis"]
        )

        with tab1:
            render_plot_container("cross_sections", st.session_state.fluorophore_df)

        with tab2:
            render_plot_container("tissue_penetration")

        with tab3:
            st.markdown("### Non-Degenerate Two-Photon Analysis")

            col1, col2 = st.columns([1, 2])
            with col1:
                # Two-photon comparison controls
                two_photon_enabled = st.toggle(
                    "Enable Non-Degenerate Analysis",
                    value=st.session_state.tissue_params.get("two_photon", {}).get(
                        "enabled", False
                    ),
                    help="Compare different wavelength combinations for non-degenerate two-photon excitation",
                )

                if two_photon_enabled:
                    st.markdown("#### Wavelength Selection")
                    lambda_a = st.number_input(
                        "λ₁ (nm)",
                        min_value=800,
                        max_value=2400,
                        value=st.session_state.tissue_params.get("two_photon", {}).get(
                            "lambda_a", 800
                        ),
                        step=5,
                        help="First excitation wavelength",
                    )
                    lambda_b = st.number_input(
                        "λ₂ (nm)",
                        min_value=800,
                        max_value=2400,
                        value=st.session_state.tissue_params.get("two_photon", {}).get(
                            "lambda_b", 1040
                        ),
                        step=5,
                        help="Second excitation wavelength",
                    )

                    # Calculate and show effective wavelength
                    lambda_c = round((2 / ((1 / lambda_a) + (1 / lambda_b))) / 5) * 5
                    st.info(f"Effective Two-Photon Wavelength: {lambda_c} nm")

                    # Update session state
                    st.session_state.tissue_params["two_photon"] = {
                        "enabled": two_photon_enabled,
                        "lambda_a": lambda_a,
                        "lambda_b": lambda_b,
                    }

            with col2:
                if two_photon_enabled:
                    st.markdown("#### Analysis Results")
                    # Here we'll add the visualization later
                    st.info("Visualization of non-degenerate excitation coming soon!")
                else:
                    st.markdown(
                        """
                        ### About Non-Degenerate Two-Photon Excitation
                        
                        Non-degenerate two-photon excitation uses two different wavelengths 
                        (λ₁ and λ₂) to achieve excitation. This can offer several advantages:
                        
                        1. **Flexibility**: Choose wavelengths that better penetrate tissue
                        2. **Efficiency**: Potentially higher cross-sections
                        3. **Reduced damage**: Lower average power at each wavelength
                        
                        Enable the analysis to explore different wavelength combinations.
                    """
                    )

    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error("An unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
