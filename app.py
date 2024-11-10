"""Main application module for Deep Tissue Imaging Optimizer."""
import logging
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.api.search_form import render_search_panel
from src.components.fluorophore_viewer import render_fluorophore_viewer
from src.components.laser_manager import render_laser_manager
from src.config.tissue_config import DEFAULT_TISSUE_PARAMS, render_math_view
from src.plots.cross_section_plot import (create_cross_section_plot,
                                          get_marker_settings,
                                          marker_settings_ui)
from src.plots.tissue_view import (calculate_tissue_parameters,
                                   create_tissue_plot)
from src.state.session_state import initialize_session_state
from src.utils.data_loader import load_cross_section_data
from src.api.google import fetch_data, send_data


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
                    # Get or initialize visibility settings in session state
                    if "fluorophore_visibility" not in st.session_state:
                        st.session_state.fluorophore_visibility = {
                            row["Name"]: True for _, row in df.iterrows()
                        }
                    
                    # Add visibility column to the DataFrame
                    df_with_visibility = df.copy()
                    df_with_visibility["Visible"] = df_with_visibility["Name"].map(
                        st.session_state.fluorophore_visibility
                    ).fillna(True)
                    
                    # Create filtered dataframe based on visibility
                    visible_df = df_with_visibility[df_with_visibility["Visible"]]
                    
                    # Plot with visible fluorophores only
                    markers_dict = get_marker_settings()
                    fig = create_cross_section_plot(
                        visible_df[["Name", "Wavelength", "Cross_Section", "Reference"]],  # Only pass required columns
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
            
            # Add the table with visibility toggles
            st.markdown("### Fluorophore Data")
            if "fluorophore_df" in st.session_state:
                # Add Hide/Show All toggle
                show_all = st.toggle(
                    "Show All Fluorophores",
                    value=True,  # Default to showing all
                    key="show_all_fluorophores"
                )
                
                # Add visibility column to the editor
                df_for_editor = st.session_state.fluorophore_df.copy()
                
                # Update all visibility states if show_all changes
                if show_all:
                    st.session_state.fluorophore_visibility = {
                        name: True for name in df_for_editor["Name"]
                    }
                else:
                    st.session_state.fluorophore_visibility = {
                        name: False for name in df_for_editor["Name"]
                    }
                
                df_for_editor["Visible"] = df_for_editor["Name"].map(
                    st.session_state.fluorophore_visibility
                ).fillna(True)
                
                edited_df = st.data_editor(
                    df_for_editor,
                    num_rows="dynamic",
                    column_config={
                        "Visible": st.column_config.CheckboxColumn(
                            "Show",
                            help="Toggle fluorophore visibility in plot",
                            default=True,
                        ),
                        "Name": st.column_config.TextColumn(
                            "Fluorophore",
                            help="Fluorophore name",
                        ),
                        "Wavelength": st.column_config.NumberColumn(
                            "2P λ (nm)",
                            help="Two-photon excitation wavelength",
                            format="%d"
                        ),
                        "Cross_Section": st.column_config.NumberColumn(
                            "Cross Section (GM)",
                            help="Two-photon cross section in Goeppert-Mayer units",
                            format="%.2f"
                        ),
                        "Reference": st.column_config.TextColumn(
                            "Reference",
                            help="Data source (Zipfel Lab or FPbase)"
                        ),
                    },
                    column_order=["Visible", "Name", "Wavelength", "Cross_Section", "Reference"],
                    use_container_width=True,
                    hide_index=True,
                    key="overview_editor"
                )
                
                # Update visibility settings from edited dataframe
                st.session_state.fluorophore_visibility = {
                    row["Name"]: row["Visible"] 
                    for _, row in edited_df.iterrows()
                }
                
                # Save button (save without visibility column)
                if st.button("💾 Save Changes", type="primary", key="overview_save"):
                    try:
                        # Remove visibility column before saving
                        save_df = edited_df.drop(columns=["Visible"])
                        st.session_state.fluorophore_df = save_df
                        
                        # Save to Google Sheets
                        data = save_df.to_dict('records')
                        send_data("fluorophores", data)
                        
                        # Backup to CSV
                        save_df.to_csv("data/fluorophores.csv", index=False)
                        
                        st.success("Changes saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save changes: {str(e)}")
                
                # Download button (without visibility column)
                csv = edited_df.drop(columns=["Visible"]).to_csv(index=False)
                st.download_button(
                    label="📥 Download Table",
                    data=csv,
                    file_name="fluorophore_table.csv",
                    mime="text/csv",
                    key="overview_download"
                )
            else:
                st.info("No data in fluorophore table yet. Add fluorophores from the Fluorophore Library tab.")
            
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
        # Page configuration with favicon
        st.set_page_config(
            page_title="Deep Tissue Imaging Optimizer",
            layout="wide",
            initial_sidebar_state="expanded",
            page_icon="src/assets/favicon.png"
        )

        # Initialize session state
        initialize_session_state()

        # ---- SIDEBAR ----
        with st.sidebar:
            # Logo and Title
            st.title("Deep Tissue Optimizer")
            
            # Parameters Section
            with st.expander("⚙️ Analysis Parameters", expanded=True):
                # Wavelength Settings
                st.subheader("📊 Wavelength Settings")
                wavelength_range = st.slider(
                    "Analysis Range (nm)",
                    min_value=700, max_value=2400,
                    value=st.session_state.global_params["wavelength_range"],
                    step=10,
                    help="Global wavelength range for all plots and analysis"
                )
                st.session_state.global_params["wavelength_range"] = wavelength_range

                norm_wavelength = st.number_input(
                    "Normalization λ (nm)",
                    min_value=800, max_value=2400,
                    value=st.session_state.global_params["normalization_wavelength"],
                    step=10,
                    help="Wavelength at which to normalize the photon fraction"
                )
                st.session_state.global_params["normalization_wavelength"] = norm_wavelength

                # Tissue Parameters
                st.subheader("🔬 Tissue Parameters")
                absorption_threshold = st.slider(
                    "Absorption Threshold (%)",
                    min_value=0, max_value=100,
                    value=st.session_state.global_params["absorption_threshold"],
                    help="Threshold for absorption shading"
                )
                st.session_state.global_params["absorption_threshold"] = absorption_threshold

            # Laser Manager
            with st.expander("🎯 Laser Configuration", expanded=False):
                render_laser_manager()

            # Footer
            st.markdown("---")
            st.markdown(
                """
                <div style='text-align: center; color: gray; font-size: 0.8em;'>
                Developed by Aaron Woods<br>
                Data from <a href="https://www.fpbase.org">FPbase</a>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---- MAIN CONTENT ----
        # Header
        st.markdown("""
            <h1 style='text-align: center; color: #0f4c81;'>
                Deep Tissue Imaging Optimizer
            </h1>
            <p style='text-align: center; color: #666666; margin-bottom: 2rem;'>
                Optimize your two-photon microscopy experiments with comprehensive fluorophore analysis
            </p>
        """, unsafe_allow_html=True)

        # Main Tabs
        tab1, tab2, tab3 = st.tabs([
            "📈 Cross-sections Overview", 
            "🔍 Tissue Penetration",
            "📚 Fluorophore Library"
        ])

        with tab1:
            st.markdown("""
                <h3 style='color: #0f4c81;'>Cross-sections Overview</h3>
                <p style='color: #666666;'>
                    View and compare two-photon cross-sections of different fluorophores
                </p>
            """, unsafe_allow_html=True)
            render_plot_container("cross_sections", st.session_state.fluorophore_df)

        with tab2:
            st.markdown("""
                <h3 style='color: #0f4c81;'>Tissue Penetration Analysis</h3>
                <p style='color: #666666;'>
                    Analyze tissue penetration characteristics and parameters
                </p>
            """, unsafe_allow_html=True)
            render_plot_container("tissue_penetration")

        with tab3:
            st.markdown("""
                <h3 style='color: #0f4c81;'>Fluorophore Library</h3>
                <p style='color: #666666;'>
                    Browse, search, and manage your fluorophore database
                </p>
            """, unsafe_allow_html=True)
            
            # Data Source Tabs
            lib_tab1, lib_tab2 = st.tabs([
                "📊 Cross Section Data", 
                "🔍 FPbase Search"
            ])
            
            with lib_tab1:
                st.info("""
                    Browse the complete library of two-photon cross section data.
                    Select a fluorophore to view its detailed data and add it to your main table.
                """)
                cross_sections = load_cross_section_data()
                render_fluorophore_viewer(cross_sections, key_prefix="main")
            
            with lib_tab2:
                st.info("""
                    Search the FPbase database for additional fluorophores.
                    Found proteins can be added to your main fluorophore table.
                """)
                render_search_panel(key_prefix="lib_")
            
            # Main Table Section
            st.markdown("---")
            st.markdown("""
                <h3 style='color: #0f4c81;'>Main Fluorophore Table</h3>
                <p style='color: #666666;'>
                    View and edit your collected fluorophore data from both Zipfel Lab and FPbase sources
                </p>
            """, unsafe_allow_html=True)
            
            if "fluorophore_df" in st.session_state:
                edited_df = st.data_editor(
                    st.session_state.fluorophore_df,
                    num_rows="dynamic",
                    column_config={
                        "Name": st.column_config.TextColumn(
                            "Fluorophore",
                            help="Fluorophore name",
                            required=True,
                        ),
                        "Wavelength": st.column_config.NumberColumn(
                            "2P λ (nm)",
                            help="Two-photon excitation wavelength",
                            required=True,
                            format="%d"
                        ),
                        "Cross_Section": st.column_config.NumberColumn(
                            "Cross Section (GM)",
                            help="Two-photon cross section in Goeppert-Mayer units",
                            format="%.2f"
                        ),
                        "Reference": st.column_config.TextColumn(
                            "Reference",
                            help="Data source (Zipfel Lab or FPbase)"
                        ),
                    },
                    column_order=["Name", "Wavelength", "Cross_Section", "Reference"],
                    use_container_width=True,
                    hide_index=True,
                    key="library_editor"
                )
                
                # Table Actions
                col1, col2, _ = st.columns([1, 1, 2])
                with col1:
                    if st.button("💾 Save Changes", type="primary", key="library_save"):
                        try:
                            # Update session state
                            st.session_state.fluorophore_df = edited_df
                            
                            # Save to Google Sheets
                            data = edited_df.to_dict('records')
                            send_data("fluorophores", data)
                            
                            # Backup to CSV
                            edited_df.to_csv("data/fluorophores.csv", index=False)
                            
                            st.success("Changes saved!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to save changes: {str(e)}")
                
                with col2:
                    csv = edited_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Table",
                        data=csv,
                        file_name="fluorophore_table.csv",
                        mime="text/csv",
                        key="library_download"
                    )
            else:
                st.warning("No data in main fluorophore table yet. Add fluorophores from above.")

    except Exception as e:
        logger.error("Unexpected application error: %s", str(e))
        st.error("An unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
