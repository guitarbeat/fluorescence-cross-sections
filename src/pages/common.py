"""Common functionality for Streamlit pages."""

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.components.ui_components import (
    render_error_boundary,
    render_plot_with_settings,
    render_data_editor,
    render_save_button,
)
from src.config.ui_config import (
    UI_TEXTS,
    FLUOROPHORE_COLUMN_CONFIG,
    FLUOROPHORE_COLUMN_ORDER,
    PLOT_CONFIG,
)
from src.plots.cross_section_plot import create_cross_section_plot, get_marker_settings, marker_settings_ui
from src.plots.tissue_view import calculate_tissue_parameters, create_tissue_plot
from src.services.fluorophore_service import (
    FluorophoreService,
    PlotDataService,
)

logger = logging.getLogger(__name__)

@st.cache_data(ttl=300)
def get_cached_tissue_data(
    wavelengths: np.ndarray,
    depth: float,
    norm_wavelength: float,
) -> dict:
    """Cache tissue calculations to improve performance."""
    return calculate_tissue_parameters(
        wavelengths=wavelengths,
        depth=depth,
        normalization_wavelength=norm_wavelength,
    )


def _render_cross_sections_plot(df: pd.DataFrame) -> None:
    """Render the cross-sections plot with settings."""
    if df is None or df.empty:
        st.info("No fluorophore data available")
        return

    # Prepare plot data
    plot_data = PlotDataService.prepare_cross_section_plot_data(df)
    if plot_data.empty:
        st.info("No visible fluorophores to plot")
        return

    # Get plot parameters
    params = PlotDataService.get_plot_parameters()

    # Create plot
    markers_dict = get_marker_settings()
    fig = create_cross_section_plot(
        plot_data,
        markers_dict=markers_dict,
        normalization_wavelength=params["normalization_wavelength"],
        depth=params["depth"],
        wavelength_range=params["wavelength_range"],
        absorption_threshold=params["absorption_threshold"],
    )

    # Simple plot rendering without settings to avoid column nesting
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme="streamlit",
        config={"displayModeBar": True, "responsive": True},
    )


def _render_fluorophore_data_editor() -> None:
    """Render the fluorophore data editor section."""
    if "fluorophore_df" not in st.session_state:
        st.info(UI_TEXTS["messages"]["no_fluorophore_data"])
        return

    # Toggle for showing all fluorophores
    show_all = st.toggle(
        UI_TEXTS["labels"]["show_all_fluorophores"],
        value=True,
        key="show_all_fluorophores",
        help=UI_TEXTS["help_texts"]["show_all_fluorophores"]
    )

    # Prepare data for editor
    df_for_editor = st.session_state.fluorophore_df.copy()
    FluorophoreService.update_fluorophore_visibility(df_for_editor, show_all)
    df_for_editor = FluorophoreService.prepare_data_for_editor(df_for_editor)

    # Convert column config to Streamlit format
    column_config = {}
    for col, config in FLUOROPHORE_COLUMN_CONFIG.items():
        if config["type"] == "checkbox":
            column_config[col] = st.column_config.CheckboxColumn(
                config["label"],
                help=config["help"],
                default=config["default"],
            )
        elif config["type"] == "text":
            column_config[col] = st.column_config.TextColumn(
                config["label"],
                help=config["help"],
            )
        elif config["type"] == "number":
            column_config[col] = st.column_config.NumberColumn(
                config["label"],
                help=config["help"],
                format=config["format"],
            )

    # Render data editor
    edited_df = render_data_editor(
        df=df_for_editor,
        column_config=column_config,
        column_order=FLUOROPHORE_COLUMN_ORDER,
        key="overview_editor",
        title=UI_TEXTS["titles"]["fluorophore_data"]
    )

    # Update visibility from editor
    FluorophoreService.update_visibility_from_editor(edited_df)

    # Save button
    def save_function():
        return FluorophoreService.save_fluorophore_data(edited_df)

    render_save_button(
        save_function=save_function,
        success_message=UI_TEXTS["messages"]["changes_saved"],
        button_text=UI_TEXTS["labels"]["save_changes"],
        button_type="primary",
        key="overview_save"
    )


def _render_tissue_penetration_plot() -> None:
    """Render the tissue penetration plot."""
    params = PlotDataService.get_plot_parameters()

    wavelengths = np.linspace(params["wavelength_range"][0], params["wavelength_range"][1], 1000)
    tissue_data = get_cached_tissue_data(
        wavelengths=wavelengths,
        depth=params["depth"],
        norm_wavelength=params["normalization_wavelength"],
    )

    # Use the original tissue plot function
    fig = create_tissue_plot(
        wavelengths=wavelengths,
        tissue_data=tissue_data,
        normalization_wavelength=params["normalization_wavelength"],
        absorption_threshold=params["absorption_threshold"],
        wavelength_range=params["wavelength_range"],
        depth=params["depth"],
    )

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def render_plot_container(plot_type: str, df: Optional[pd.DataFrame] = None) -> None:
    """Render plot containers with consistent error handling."""
    try:
        if "tissue_params" not in st.session_state:
            from src.config.tissue_config import DEFAULT_TISSUE_PARAMS
            st.session_state.tissue_params = DEFAULT_TISSUE_PARAMS.copy()

        plot_container = st.container(border=True)

        with plot_container:
            if plot_type == "cross_sections":
                _render_cross_sections_plot(df)
                _render_fluorophore_data_editor()

            elif plot_type == "tissue_penetration":
                _render_tissue_penetration_plot()

    except (ValueError, KeyError) as e:
        logger.error("Error rendering %s plot: %s", plot_type, str(e))
        st.error(f"Error creating {plot_type} plot: {str(e)}")
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error rendering %s plot: %s", plot_type, str(e))
        st.error("An unexpected error occurred. Please check the logs.")


def render_footer() -> None:
    """Render a simple application footer."""
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em; padding: 20px 0;'>
            Developed by Aaron Woods<br>
            Data from <a href="https://www.fpbase.org">FPbase</a>
        </div>
        """,
        unsafe_allow_html=True,
    )
