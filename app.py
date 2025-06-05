"""Main application module for Deep Tissue Imaging Optimizer."""
import logging
from typing import Optional, Literal

import numpy as np
import pandas as pd
import streamlit as st
from streamlit_scroll_navigation import scroll_navbar

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
from src.api.google import send_data
import streamlit_nested_layout  # noqa: F401
# from src.utils.styling import styled_header, styled_description # Removed as standard components are used


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sticky container configuration
MARGINS = {
    "top": "2.875rem",
    "bottom": "0",
}

STICKY_CONTAINER_HTML = """
<style>
div[data-testid="stVerticalBlock"] div:has(div.fixed-header-{i}) {{
    position: sticky;
    {position}: {margin};
    background-color: var(--background-color);
    z-index: 999;
}}
/* Push main content down to avoid overlap */
.main .block-container {{
    padding-top: 4rem;
}}
</style>
<div class='fixed-header-{i}'/>
""".strip()

# Not to apply the same style to multiple containers
count = 0


def sticky_container(
    *,
    height: int | None = None,
    border: bool | None = None,
    mode: Literal["top", "bottom"] = "top",
    margin: str | None = None,
):
    """Create a sticky container that stays visible during scrolling."""
    if margin is None:
        margin = MARGINS[mode]

    global count
    html_code = STICKY_CONTAINER_HTML.format(
        position=mode, margin=margin, i=count)
    count += 1

    container = st.container(height=height, border=border)
    container.markdown(html_code, unsafe_allow_html=True)
    return container


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

        # Set fixed square size
        PLOT_SIZE = 800  # Size in pixels for both width and height

        if plot_type == "cross_sections":
            # Direct container instead of expander since it was always expanded
            plot_container = st.container(border=True)
            with plot_container:
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
                        visible_df[["Name", "Wavelength",
                                    "Cross_Section", "Reference"]],
                        markers_dict=markers_dict,
                        normalization_wavelength=norm_wavelength,
                        depth=depth,
                        wavelength_range=wavelength_range,
                        absorption_threshold=absorption_threshold,
                    )

                    # Let Plotly handle the sizing while maintaining aspect ratio
                    st.plotly_chart(
                        fig,
                        use_container_width=True,  # Fill container width
                        theme="streamlit",         # Use Streamlit theme
                        config={
                            'displayModeBar': True,
                            'responsive': True     # Enable responsive behavior
                        }
                    )
                else:
                    st.info("No data to display - try searching for fluorophores.")

                # Marker settings in a popover (keeping this as it's appropriate)
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
                    column_order=["Visible", "Name",
                                  "Wavelength", "Cross_Section", "Reference"],
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
                if st.button("Save Changes", icon="💾", type="primary", key="overview_save"):
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
                    label="Download Table",
                    icon="📥",
                    data=csv,
                    file_name="fluorophore_table.csv",
                    mime="text/csv",
                    key="overview_download"
                )
            else:
                st.info(
                    "No data in fluorophore table yet. Add fluorophores from the Fluorophore Library tab.")

        elif plot_type == "tissue_penetration":
            # Direct container instead of expander since it was always expanded
            plot_container = st.container(border=True)
            with plot_container:
                # Calculate tissue parameters with caching
                wavelengths = np.linspace(
                    wavelength_range[0], wavelength_range[1], 1000)
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
                # Update layout to force square aspect ratio
                fig.update_layout(
                    width=PLOT_SIZE,
                    height=PLOT_SIZE,  # Make height equal to width
                    autosize=False,  # Disable autosize to maintain square shape
                )
                st.plotly_chart(fig, use_container_width=True,
                                theme="streamlit")
            render_math_view()

    except (ValueError, KeyError) as e:
        logger.error("Error rendering %s plot: %s", plot_type, str(e))
        st.error(f"Error creating {plot_type} plot: {str(e)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error rendering %s plot: %s",
                     plot_type, str(e))
        st.error("An unexpected error occurred. Please check the logs.")




def main() -> None:
    """Main application function."""
    try:
        # Page configuration
        st.set_page_config(
            page_title="Deep Tissue Imaging Optimizer",
            layout="wide",
            initial_sidebar_state="collapsed",
            page_icon="src/assets/favicon.png"
        )

        # Initialize session state
        initialize_session_state()

        # Add query parameter handling
        params = st.query_params

        # Set initial wavelength from URL if provided
        if "wavelength" in params:
            try:
                wavelength = float(params["wavelength"])
                st.session_state.global_params["normalization_wavelength"] = wavelength
            except ValueError:
                st.warning("Invalid wavelength parameter in URL")

                # ---- MAIN CONTENT ----
        # Title with consistent styling
        st.header("Deep Tissue Optimizer")

        # ---- STICKY HORIZONTAL NAVIGATION BAR ----
        with sticky_container(mode="top", border=False):
            # Navigation links with updated sections
            scroll_navbar(
                anchor_ids=["lasers", "wavelength", "tissue_params",
                            "cross_sections", "tissue", "library"],
                anchor_labels=["Laser Configuration", "Wavelength Settings", "Tissue Parameters",
                               "Cross-sections", "Tissue Penetration", "Fluorophore Discovery"],
                anchor_icons=["bullseye", "rulers", "microscope",
                              "graph-up", "lungs", "collection"],
                orientation="horizontal",
                key="main_nav"
            )

        # Sections with consistent styling
        st.divider()
        st.header("Laser Configuration", anchor="lasers",
                  help="Configure and manage laser settings")
        # Direct container instead of expander since it was always expanded
        laser_container = st.container(border=True)
        with laser_container:
            st.caption(
                "Configure and manage laser settings for visualization"
            )
            render_laser_manager()

        st.divider()
        st.header("Wavelength Settings", anchor="wavelength",
                  help="Configure global wavelength parameters")
        # Use container with border for better visual separation
        wavelength_container = st.container(border=True)
        with wavelength_container:
            st.caption(
                "Configure global wavelength range and normalization settings"
            )

            col1, col2 = st.columns(2)
            with col1:
                wavelength_range = st.slider(
                    "Analysis Range (nm)",
                    min_value=700, max_value=2400,
                    value=st.session_state.global_params["wavelength_range"],
                    step=10,
                    help="Global wavelength range for all plots and analysis"
                )
                st.session_state.global_params["wavelength_range"] = wavelength_range
            with col2:
                norm_wavelength = st.number_input(
                    "Normalization λ (nm)",
                    min_value=800, max_value=2400,
                    value=st.session_state.global_params["normalization_wavelength"],
                    step=10,
                    help="Wavelength at which to normalize the photon fraction"
                )
                st.session_state.global_params["normalization_wavelength"] = norm_wavelength

        # ---- TISSUE PARAMETERS SECTION ----
        st.divider()
        st.header("Tissue Parameters", anchor="tissue_params",
                  help="Configure tissue-specific parameters")

        # Use tabs to organize tissue parameters better
        general_tab, absorption_tab, scattering_tab = st.tabs([
            "🔬 General Settings",
            "💧 Absorption Properties",
            "🌊 Scattering Properties"
        ])

        with general_tab:
            st.caption("Configure general tissue analysis parameters")

            col1, col2 = st.columns(2)
            with col1:
                # Depth control
                depth = st.session_state.tissue_params.get(
                    "depth", DEFAULT_TISSUE_PARAMS["depth"])
                new_depth = st.slider(
                    "Tissue Depth (mm)",
                    min_value=0.1, max_value=2.0,
                    value=depth, step=0.1,
                    help="Distance light travels through tissue",
                    key="tissue_depth_main"
                )
                if new_depth != depth:
                    st.session_state.tissue_params["depth"] = new_depth

            with col2:
                absorption_threshold = st.slider(
                    "Absorption Threshold (%)",
                    min_value=0, max_value=100,
                    value=st.session_state.global_params["absorption_threshold"],
                    help="Threshold for absorption shading"
                )
                st.session_state.global_params["absorption_threshold"] = absorption_threshold

        with absorption_tab:
            st.caption("Configure water content and absorption properties")

            # Water content control with unique key
            water_content = st.select_slider(
                "Water Content",
                options=[i / 100 for i in range(0, 105, 5)],
                value=st.session_state.tissue_params.get(
                    "water_content", DEFAULT_TISSUE_PARAMS["water_content"]),
                help="Fraction of tissue that is water (≈75% for brain)",
                key="absorption_water_content"
            )
            st.session_state.tissue_params["water_content"] = water_content

            # Show water absorption info
            st.info("""
                **Water Absorption Properties:**
                - Controls absorption strength linearly
                - Brain tissue ≈ 75% water
                - Major absorption peaks at 1450nm and 1950nm
                - Formula: μₐ(λ) = μₐᵏ(λ) × water_content
            """)

        with scattering_tab:
            st.caption("Configure anisotropy, scattering power, and amplitude")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Anisotropy control with unique key
                g = st.slider(
                    "Anisotropy (g)",
                    0.0, 1.0,
                    st.session_state.tissue_params.get(
                        "g", DEFAULT_TISSUE_PARAMS["g"]),
                    0.05,
                    help="Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
                    key="scattering_anisotropy"
                )
                st.session_state.tissue_params["g"] = g

            with col2:
                # Scattering power control with unique key
                b = st.number_input(
                    "Scattering Power (b)",
                    min_value=0.5, max_value=2.0,
                    value=st.session_state.tissue_params.get(
                        "b", DEFAULT_TISSUE_PARAMS["b"]),
                    step=0.05,
                    help="Wavelength dependence (≈1.37 for brain tissue)",
                    key="scattering_power"
                )
                st.session_state.tissue_params["b"] = b

            with col3:
                # Scattering scale control with unique key
                a = st.number_input(
                    "Scattering Scale (a)",
                    min_value=0.5, max_value=2.0,
                    value=st.session_state.tissue_params.get(
                        "a", DEFAULT_TISSUE_PARAMS["a"]),
                    step=0.1,
                    help="Scattering amplitude [mm⁻¹]",
                    key="scattering_scale"
                )
                st.session_state.tissue_params["a"] = a

            # Show scattering info
            st.info("""
                **Light Scattering Properties:**
                - **Anisotropy (g)**: Controls scattering direction (brain ≈ 0.9)
                - **Power (b)**: Wavelength dependence (brain ≈ 1.37)  
                - **Scale (a)**: Overall scattering strength (brain ≈ 1.1 mm⁻¹)
                - Formula: μₛ(λ) = a/(1-g) × (λ/500)⁻ᵇ
            """)

        # ---- CROSS SECTIONS SECTION ----
        st.divider()
        st.header("Cross-sections Overview", anchor="cross_sections",
                  help="Compare two-photon cross-sections of different fluorophores")
        st.caption(
            "View and compare two-photon cross-sections of different fluorophores")
        render_plot_container(
            "cross_sections", st.session_state.fluorophore_df)

        # ---- TISSUE PENETRATION SECTION ----
        st.divider()
        st.header("Tissue Penetration Analysis", anchor="tissue",
                  help="Analyze how light penetrates through tissue")
        st.caption("Analyze tissue penetration characteristics and parameters")
        render_plot_container("tissue_penetration")

        # ---- LIBRARY SECTION ----
        st.divider()
        st.header("Fluorophore Discovery", anchor="library",
                  help="Browse and search fluorophore database")
        st.caption("Browse, search, and manage your fluorophore database")
        # Data Source Tabs (keeping tabs for this subsection)
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

        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='
                text-align: center;
                color: gray;
                font-size: 0.8em;
                padding: 20px 0;
            '>
                Developed by Aaron Woods<br>
                Data from <a href="https://www.fpbase.org">FPbase</a>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:
        logger.error("Unexpected application error: %s", str(e))
        st.error("An unexpected error occurred. Please check the logs.")


if __name__ == "__main__":
    main()
