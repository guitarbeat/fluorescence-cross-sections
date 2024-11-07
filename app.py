"""Main application module for Deep Tissue Imaging Optimizer."""
import logging
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.api.search_form import render_search_panel
from src.components.fluorophore_manager import render_fluorophore_manager
from src.components.laser_manager import render_laser_manager
from src.config.tissue_config import DEFAULT_TISSUE_PARAMS, render_math_view
from src.plots.cross_section_plot import (create_cross_section_plot,
                                          get_marker_settings,
                                          marker_settings_ui)
from src.plots.tissue_view import (calculate_tissue_parameters,
                                   create_tissue_plot)
from src.state.session_state import initialize_session_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_tissue_data(
    wavelengths: np.ndarray,
    depth: float,
    norm_wavelength: float,
) -> dict:
    """
    Cache tissue calculations to improve performance.

    Args:
        wavelengths: Array of wavelengths to calculate parameters for
        depth: Tissue depth in mm
        norm_wavelength: Wavelength for normalization

    Returns:
        Dictionary containing calculated tissue parameters
    """
    return calculate_tissue_parameters(
        wavelengths=wavelengths,
        depth=depth,
        normalization_wavelength=norm_wavelength,
    )


def render_plot_container(plot_type: str, df: Optional[pd.DataFrame] = None) -> None:
    """Render plot containers with consistent error handling."""
    try:
        # Ensure tissue_params are initialized
        if "tissue_params" not in st.session_state:
            st.session_state.tissue_params = DEFAULT_TISSUE_PARAMS.copy()

        # Get parameters from session state
        global_params = st.session_state.global_params
        tissue_params = st.session_state.tissue_params
        depth = tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
        norm_wavelength = global_params["normalization_wavelength"]
        wavelength_range = global_params["wavelength_range"]
        absorption_threshold = global_params["absorption_threshold"]

        if plot_type == "cross_sections":
            with st.expander("Cross-sections Overview", expanded=True):
                if df is not None and not df.empty:
                    markers_dict = get_marker_settings()
                    fig = create_cross_section_plot(
                        df,
                        markers_dict=markers_dict,
                        normalization_wavelength=norm_wavelength,
                        depth=depth,
                        wavelength_range=wavelength_range,
                        absorption_threshold=absorption_threshold,
                    )
                    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
                else:
                    st.info("No data to display - try searching for fluorophores.")
                with st.popover("Marker Settings"):
                    marker_settings_ui()
            render_fluorophore_manager()
            
        elif plot_type == "tissue_penetration":
            with st.expander("Tissue Penetration", expanded=True):
                # Calculate tissue parameters with caching
                wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], 1000)
                tissue_data = get_cached_tissue_data(
                    wavelengths=wavelengths,
                    depth=depth,
                    norm_wavelength=norm_wavelength
                )

                fig = create_tissue_plot(
                    wavelengths=wavelengths,
                    tissue_data=tissue_data,
                    normalization_wavelength=norm_wavelength,
                    absorption_threshold=absorption_threshold,
                    wavelength_range=wavelength_range,
                    depth=depth
                )
                st.plotly_chart(fig, use_container_width=True, theme="streamlit")
            render_math_view()

    except (ValueError, KeyError) as e:
        logger.error("Error rendering %s plot: %s", plot_type, str(e))
        st.error(f"Error creating {plot_type} plot: {str(e)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error rendering %s plot: %s", plot_type, str(e))
        st.error("An unexpected error occurred. Please check the logs.")


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

    except (ValueError, KeyError) as e:
        logger.error("Application error: %s", str(e))
        st.error(f"Configuration error: {str(e)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected application error: %s", str(e))
        st.error("An unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
