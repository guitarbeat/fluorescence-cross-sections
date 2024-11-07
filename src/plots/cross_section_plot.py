from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..components.laser_manager import overlay_lasers
from ..config.plot_config import CrossSectionPlotConfig
from ..plots.tissue_view import calculate_tissue_parameters
from ..config.tissue_config import DEFAULT_TISSUE_PARAMS


def get_marker_settings() -> Dict[str, Tuple[str, str]]:
    """Get marker settings from session state or initialize defaults."""
    if "marker_settings" not in st.session_state:
        config = CrossSectionPlotConfig()
        st.session_state.marker_settings = config.default_marker_styles
    return st.session_state.marker_settings


def marker_settings_ui() -> None:
    """Render UI for customizing marker settings."""
    if not st.session_state.get("marker_settings"):
        return


    # Create two columns for the entire interface
    main_col, preview_col = st.columns([3, 1])
    
    with main_col:
        # Define marker options
        marker_options = {
            "● Circle": "circle",
            "■ Square": "square",
            "◆ Diamond": "diamond",
            "▲ Triangle": "triangle-up",
            "▼ Down Triangle": "triangle-down",
            "★ Star": "star",
            "⬡ Hexagon": "hexagon",
        }
        marker_list = list(marker_options.keys())

        # Create a row for each reference
        for ref in st.session_state.marker_settings.keys():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                current_marker = st.session_state.marker_settings[ref][0]
                marker_idx = list(marker_options.values()).index(current_marker)
                marker = st.selectbox(
                    ref,
                    options=marker_list,
                    index=marker_idx,
                    key=f"marker_{ref}",
                    label_visibility="collapsed"
                )
                st.session_state.marker_settings[ref] = (
                    marker_options[marker],
                    st.session_state.marker_settings[ref][1],
                )
            
            with col2:
                st.markdown(f"<small>{ref}</small>", unsafe_allow_html=True)
            
            with col3:
                color = st.color_picker(
                    "Color",
                    value=st.session_state.marker_settings[ref][1],
                    key=f"color_{ref}",
                    label_visibility="collapsed"
                )
                st.session_state.marker_settings[ref] = (
                    st.session_state.marker_settings[ref][0],
                    color,
                )


    with preview_col:
        
        st.button("Reset to Defaults", use_container_width=True, 
                 on_click=lambda: reset_marker_settings(st.session_state.marker_settings.keys()))

        # Show compact preview with just reference names in their colors
        for ref, (_, color) in st.session_state.marker_settings.items():
            st.markdown(
                f"<div style='text-align: left; color: {color};'>"
                f"{ref}</div>",  # Just show first word of reference
                unsafe_allow_html=True,
            )
            
                # Add reset button


def reset_marker_settings(refs):
    """Reset marker settings to defaults."""
    default_markers = ["circle", "square", "diamond", "triangle-up", "triangle-down", "star"]
    default_colors = ["#00008B", "#000000", "#FFC0CB", "#008080", "#808080", "#4B0082"]
    
    st.session_state.marker_settings = {
        ref: (
            default_markers[i % len(default_markers)],
            default_colors[i % len(default_colors)],
        )
        for i, ref in enumerate(refs)
    }
    st.rerun()


def create_cross_section_plot(
    df: pd.DataFrame,
    markers_dict: Optional[Dict[str, Tuple[str, str]]] = None,
    normalization_wavelength: float = 1300,
    depth: float = None,
    wavelength_range: Tuple[float, float] = None,
    absorption_threshold: float = 50,
) -> go.Figure:
    """Create cross section plot with consistent styling."""
    config = CrossSectionPlotConfig()
    if wavelength_range:
        config.wavelength_range = wavelength_range

    # Get depth from session state if not provided
    if depth is None:
        depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])

    threshold_norm = absorption_threshold / 100

    # Create figure
    fig = go.Figure()

    # Calculate normalized photon fraction for background
    wavelengths = np.linspace(
        config.wavelength_range[0], config.wavelength_range[1], 100
    )
    tissue_data = calculate_tissue_parameters(wavelengths, depth=depth)

    # Normalize at specified wavelength
    norm_idx = np.abs(wavelengths - normalization_wavelength).argmin()
    norm_factor = tissue_data["T"][norm_idx]
    photon_fraction = tissue_data["T"] / norm_factor

    # Get y-axis range from data
    min_y = df["Cross_Section"].min() * 0.8  # Add 20% padding below
    max_y = df["Cross_Section"].max() * 1.2  # Add 20% padding above

    # Create background heatmap with extended y range
    y_values = np.logspace(np.log10(min_y), np.log10(max_y), 100)
    Z = np.tile(photon_fraction, (len(y_values), 1))

    # Update colorscale based on threshold
    config.heatmap_colorscale[2][0] = threshold_norm

    # Add heatmap
    fig.add_trace(
        go.Heatmap(
            x=wavelengths,
            y=y_values,
            z=Z,
            colorscale=config.heatmap_colorscale,
            showscale=True,
            colorbar=dict(
                title="Normalized<br>Photon<br>Fraction",
                tickvals=[0.01, threshold_norm, 1.0],
                ticktext=["0.01", f"{absorption_threshold}%", "100%"],
                len=0.5,
                y=0.5,
                yanchor="top",
            ),
            zmin=0.01,
            zmax=1.0,
            opacity=config.heatmap_opacity,
        )
    )

    # Add scatter points for each reference
    for ref in df["Reference"].unique():
        ref_data = df[df["Reference"] == ref]
        marker_style, color = markers_dict.get(
            ref, config.default_marker_styles.get(ref, ("circle", "#808080"))
        )

        fig.add_trace(
            go.Scatter(
                x=ref_data["Wavelength"],
                y=ref_data["Cross_Section"],
                mode="markers+text",
                name=ref,
                marker=dict(
                    symbol=marker_style,
                    size=config.marker_size,
                    color=color,
                ),
                text=ref_data["Name"],
                textposition="top center",
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Wavelength: %{x} nm<br>"
                    "Cross Section: %{y} GM<br>"
                    "<extra></extra>"
                ),
            )
        )

    # Add laser overlays
    fig = overlay_lasers(fig, plot_type="cross_section")

    # Update layout with log scale and proper ranges
    layout = config.get_layout()
    layout.update(
        yaxis=dict(
            type="log",
            range=[np.log10(min_y), np.log10(max_y)],
            title="Peak 2PA Cross Section (GM)",
        ),
        xaxis=dict(
            title="Wavelength (nm)",
            range=[config.wavelength_range[0], config.wavelength_range[1]],
        ),
    )
    fig.update_layout(layout)

    return fig
