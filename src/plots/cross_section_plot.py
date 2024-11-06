from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..components.laser_manager import overlay_lasers
from ..models.plot_config import get_theme_colors
from ..models.tissue_model import calculate_tissue_parameters


def get_marker_settings() -> Dict[str, Tuple[str, str]]:
    """Get marker settings from session state or initialize defaults."""
    if "marker_settings" not in st.session_state:
        st.session_state.marker_settings = {
            "Dana et al. (2016)": ("circle", "#00008B"),  # darkblue in hex
            "Drobizhev et al. (2011)": ("square", "#000000"),  # black in hex
            "Janelia, Harris Lab": ("diamond", "#FFC0CB"),  # pink in hex
            "Kobat et al. (2009)": ("triangle-up", "#008080"),  # teal in hex
            "Xu et al. (1996)": ("triangle-down", "#808080"),  # gray in hex
        }
    return st.session_state.marker_settings


def marker_settings_ui() -> None:
    """Render UI for customizing marker settings."""
    if not st.session_state.get("marker_settings"):
        return

    with st.expander("Reference Style Settings", expanded=False):
        # Create columns for better organization
        col1, col2 = st.columns([1, 1])

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

        with col1:
            st.markdown("##### Marker Styles")

            # Show marker options only for references in the data
            for ref in st.session_state.marker_settings.keys():
                current_marker = st.session_state.marker_settings[ref][0]
                marker_idx = list(marker_options.values()).index(current_marker)
                marker = st.selectbox(
                    ref,
                    options=marker_list,
                    index=marker_idx,
                    key=f"marker_{ref}",
                    help=f"Select marker style for {ref}",
                )
                st.session_state.marker_settings[ref] = (
                    marker_options[marker],
                    st.session_state.marker_settings[ref][1],
                )

        with col2:
            st.markdown("##### Color Scheme")
            # Show color pickers for each reference
            for ref in st.session_state.marker_settings.keys():
                color = st.color_picker(
                    ref,
                    value=st.session_state.marker_settings[ref][1],
                    key=f"color_{ref}",
                    help=f"Choose color for {ref}",
                )
                st.session_state.marker_settings[ref] = (
                    st.session_state.marker_settings[ref][0],
                    color,
                )

        # Add reset button
        if st.button("Reset to Defaults", use_container_width=True):
            # Reset to default styles for current references
            default_markers = [
                "circle",
                "square",
                "diamond",
                "triangle-up",
                "triangle-down",
                "star",
            ]
            default_colors = [
                "#00008B",
                "#000000",
                "#FFC0CB",
                "#008080",
                "#808080",
                "#4B0082",
            ]

            st.session_state.marker_settings = {
                ref: (
                    default_markers[i % len(default_markers)],
                    default_colors[i % len(default_colors)],
                )
                for i, ref in enumerate(st.session_state.marker_settings.keys())
            }
            st.rerun()

        # Show preview of current settings
        st.markdown("##### Current Settings Preview")
        preview_cols = st.columns(len(st.session_state.marker_settings))
        for i, (ref, (marker, color)) in enumerate(
            st.session_state.marker_settings.items()
        ):
            with preview_cols[i]:
                marker_symbol = [k for k, v in marker_options.items() if v == marker][0]
                st.markdown(
                    f"<div style='text-align: center; color: {color};'>"
                    f"{marker_symbol}<br>"
                    f"{ref.split()[0]}</div>",
                    unsafe_allow_html=True,
                )


def create_cross_section_plot(
    df: pd.DataFrame,
    markers_dict: Optional[Dict[str, Tuple[str, str]]] = None,
    normalization_wavelength: float = 1300,
    depth: float = 1.0,
    wavelength_range: Tuple[float, float] = (700, 1600),
) -> go.Figure:
    """Create cross section plot with consistent styling."""
    # Get theme colors and global parameters
    theme = get_theme_colors()
    absorption_threshold = st.session_state.get("global_absorption_threshold", 50)

    # Create figure
    fig = go.Figure()

    # Calculate normalized photon fraction for background using global range
    wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], 100)
    tissue_data = calculate_tissue_parameters(wavelengths, depth=depth)

    # Normalize at specified wavelength
    norm_idx = np.abs(wavelengths - normalization_wavelength).argmin()
    norm_factor = tissue_data["T"][norm_idx]
    photon_fraction = tissue_data["T"] / norm_factor

    # Create background heatmap
    y_values = np.logspace(1, 3, 100)  # Log scale from 10 to 1000 GM
    Z = np.tile(photon_fraction, (len(y_values), 1))

    # Create a custom colorscale that puts white at the absorption threshold
    threshold_norm = absorption_threshold / 100  # Convert percentage to fraction
    colorscale = [
        [0, "rgb(255, 200, 200)"],  # Light red for minimum
        [threshold_norm - 0.1, "rgb(255, 220, 220)"],  # Slightly lighter red
        [threshold_norm, "rgb(255, 255, 255)"],  # White at threshold
        [1, "rgb(200, 200, 255)"],  # Light blue for maximum
    ]

    # Add heatmap with updated colorscale
    fig.add_trace(
        go.Heatmap(
            x=wavelengths,
            y=y_values,
            z=Z,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                title="Normalized<br>Photon<br>Fraction",
                tickvals=[0.01, threshold_norm, 1.0],
                ticktext=["0.01", f"{absorption_threshold}%", "100%"],
                len=0.5,  # Make colorbar 50% of plot height
                y=0.5,  # Position colorbar near top
                yanchor="top",  # Anchor from top
            ),
            zmin=0.01,
            zmax=1.0,
            opacity=0.7,
        )
    )

    # Add scatter points for each reference
    for ref in df["Reference"].unique():
        ref_data = df[df["Reference"] == ref]
        marker_style, color = markers_dict.get(ref, ("circle", "#808080"))

        fig.add_trace(
            go.Scatter(
                x=ref_data["Wavelength"],
                y=ref_data["Cross_Section"],
                mode="markers+text",
                name=ref,
                marker=dict(
                    symbol=marker_style,
                    size=10,
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

    # Apply common styling with log scale for y-axis
    fig.update_layout(
        title=dict(
            text="Two-Photon Cross Sections", font=dict(color=theme["text_color"])
        ),
        xaxis=dict(
            title="Wavelength (nm)",
            range=wavelength_range,  # Use global range
            showgrid=True,
            gridwidth=1,
            gridcolor=theme["grid_color"],
            zeroline=False,
            tickfont=dict(color=theme["text_color"]),
            title_font=dict(color=theme["text_color"]),
        ),
        yaxis=dict(
            title="2PA Cross Section (GM)",
            type="log",
            range=[1, 3],  # Log scale from 10 to 1000 GM
            showgrid=True,
            gridwidth=1,
            gridcolor=theme["grid_color"],
            zeroline=False,
            tickfont=dict(color=theme["text_color"]),
            title_font=dict(color=theme["text_color"]),
        ),
        plot_bgcolor=theme["bg_color"],
        paper_bgcolor=theme["bg_color"],
        margin=dict(t=50, r=50, b=50, l=50),
        height=600,
        showlegend=True,
        legend=dict(bgcolor="rgba(255, 255, 255, 0.8)", title="Reference"),
    )

    return fig
