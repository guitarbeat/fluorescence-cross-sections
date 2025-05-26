import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.config.tissue_config import DEFAULT_TISSUE_PARAMS
from src.config.plot_config import STYLE_CONFIG

from ..components.laser_manager import overlay_lasers
from ..config.plot_config import TissuePlotConfig
from ..utils.data_loader import load_water_absorption_data  # Updated import

logger = logging.getLogger(__name__)


def calculate_virtual_wavelength(lambda_a: float, lambda_b: float) -> float:
    """Calculate the effective non degenerate two-photon excitation wavelength."""
    # Round to nearest 5nm as in MATLAB code
    effective_wavelength = 2 / ((1 / lambda_a) + (1 / lambda_b))
    return round(effective_wavelength / 5) * 5


def calculate_tissue_parameters(
    wavelengths: npt.NDArray[np.float64],
    g: float = None,
    a: float = None,
    water_content: float = None,
    b: float = None,
    depth: float = None,
    normalization_wavelength: float = None,
    lambda_a: Optional[float] = None,
    lambda_b: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate tissue penetration parameters using experimental data."""
    # Get parameters from session state if not provided
    if "tissue_params" not in st.session_state:
        st.session_state.tissue_params = DEFAULT_TISSUE_PARAMS.copy()
    
    params = st.session_state.tissue_params
    g = g if g is not None else params.get("g", DEFAULT_TISSUE_PARAMS["g"])
    a = a if a is not None else params.get("a", DEFAULT_TISSUE_PARAMS["a"])
    water_content = water_content if water_content is not None else params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    b = b if b is not None else params.get("b", DEFAULT_TISSUE_PARAMS["b"])
    depth = depth if depth is not None else params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
    
    # Get normalization wavelength from global params if not provided
    if normalization_wavelength is None:
        normalization_wavelength = st.session_state.global_params.get("normalization_wavelength", 1300)

    try:
        # Load water absorption data
        water_data = load_water_absorption_data()

        # Interpolate water absorption to match wavelengths
        mua = np.interp(wavelengths, water_data["wavelength"], water_data["absorption"])
        mua = mua * water_content / 10  # Scale by water content and convert units

        # Calculate scattering coefficient with safety checks
        wavelength_ratio = np.maximum(wavelengths / 500, 1e-10)  # Prevent division by zero or negative values
        mus_prime = a * np.power(wavelength_ratio, -b)  # Use safe ratio
        mus = mus_prime / (1 - g)

        # Calculate total attenuation
        total_mu = mus + mua

        # Calculate transmission and normalize
        T = np.exp(-total_mu * depth)
        norm_idx = np.abs(wavelengths - normalization_wavelength).argmin()
        T = T / T[norm_idx]  # Normalize at specified wavelength

        # Calculate water absorption percentage
        Tw = 1 - np.exp(-mua * depth)  # Match MATLAB calculation

        # Find wavelength with maximum transmission
        max_trans_wavelength = wavelengths[np.argmax(T)]

        # Calculate depth-dependent parameters
        z_range = np.arange(0, 2.1, 0.1)  # 0 to 2mm in 0.1mm steps
        z = z_range[:, np.newaxis]  # Shape (n_z, 1)
        T_z = np.exp(-(mua + mus) * z)
        T_z = T_z / T_z[:, norm_idx][:, np.newaxis]  # Normalize at each depth
        Tw_z = 1 - np.exp(-mua * z)

        # Two-photon comparison if wavelengths provided
        two_photon_data = None
        if lambda_a is not None and lambda_b is not None:
            lambda_c = calculate_virtual_wavelength(lambda_a, lambda_b)
            # Get values at specific wavelengths
            idx_a = np.abs(wavelengths - lambda_a).argmin()
            idx_b = np.abs(wavelengths - lambda_b).argmin()
            idx_c = np.abs(wavelengths - lambda_c).argmin()

            two_photon_data = {
                "wavelengths": [lambda_a, lambda_b, lambda_c],
                "T": [T[idx_a], T[idx_b], T[idx_c]],
                "Tw": [Tw[idx_a], Tw[idx_b], Tw[idx_c]],
            }

        return {
            "T": T,
            "Tw": Tw,
            "T_z": T_z,
            "Tw_z": Tw_z,
            "z_range": z_range,
            "max_transmission_wavelength": max_trans_wavelength,
            "two_photon_data": two_photon_data,
            "normalization_wavelength": normalization_wavelength,  # Add this to return dict
        }

    except Exception as e:
        logger.error(f"Error calculating tissue parameters: {e}")
        return {}


def create_tissue_plot(
    wavelengths: npt.NDArray[np.float64],
    tissue_data: Dict[str, Any],
    normalization_wavelength: float = 1300,
    absorption_threshold: float = 50,
    wavelength_range: Optional[Tuple[float, float]] = None,
    depth: float = 1.0,
) -> go.Figure:
    """Create tissue penetration plot with consistent styling."""
    config = TissuePlotConfig()
    
    # Set wavelength range from session state but extend heatmap
    if wavelength_range:
        config.wavelength_range = wavelength_range

    # Calculate extended wavelength range for heatmap
    extension_factor = 3.0  # Extend 3x beyond visible range
    range_width = wavelength_range[1] - wavelength_range[0]
    extension = range_width * (extension_factor - 1) / 2
    extended_range = (
        wavelength_range[0] - extension,
        wavelength_range[1] + extension
    )

    # Create extended wavelengths array for calculations
    extended_wavelengths = np.linspace(
        extended_range[0], 
        extended_range[1], 
        500  # Increased resolution
    )
    
    # Calculate tissue parameters for extended range
    extended_tissue_data = calculate_tissue_parameters(
        wavelengths=extended_wavelengths,
        depth=depth,
        normalization_wavelength=normalization_wavelength
    )

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Normalize photon fraction at specified wavelength
    norm_idx = np.abs(extended_wavelengths - normalization_wavelength).argmin()
    normalized_fraction = extended_tissue_data["T"] / extended_tissue_data["T"][norm_idx]

    # Add photon fraction trace using config
    fig.add_trace(
        go.Scatter(
            x=extended_wavelengths,
            y=normalized_fraction,
            name="Normalized Photon Fraction",
            line=dict(color="blue", width=2),
            showlegend=False,
            hovertemplate="Wavelength: %{x:.0f} nm<br>Fraction: %{y:.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Calculate absorption mask for extended range
    absorption = extended_tissue_data["Tw"] * 100  # Convert to percentage
    absorption_mask = absorption >= absorption_threshold

    # Find indices where absorption_mask changes
    indices = np.where(np.diff(absorption_mask.astype(int)) != 0)[0] + 1
    indices = np.concatenate(([0], indices, [len(extended_wavelengths)]))

    # Add water absorption percentage line as a single continuous trace
    fig.add_trace(
        go.Scatter(
            x=extended_wavelengths,
            y=np.minimum(absorption, 100),  # Clip absorption values to 100%
            name="Water Absorption",
            mode='lines',  # Only lines, no markers
            line=dict(
                color="red",
                width=2,
                dash="dot",  # Default to dotted line for below threshold
            ),
            showlegend=False,
            hovertemplate="Wavelength: %{x:.0f} nm<br>Absorption: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    # Add solid line overlay for above-threshold regions
    for start, end in zip(indices[:-1], indices[1:]):
        if absorption_mask[start]:
            # Add shading for absorption regions
            fig.add_shape(
                type="rect",
                x0=extended_wavelengths[start],
                x1=extended_wavelengths[end-1],
                y0=0,
                y1=1,
                fillcolor="rgba(255, 0, 0, 0.1)",
                line_width=0,
                layer="below",
                yref="paper"  # Use paper coordinates for full height
            )
            # Add solid line overlay
            fig.add_trace(
                go.Scatter(
                    x=extended_wavelengths[start:end],
                    y=np.minimum(absorption[start:end], 100),
                    mode='lines',
                    line=dict(color="red", width=2),
                    showlegend=False,
                    hovertemplate="Wavelength: %{x:.0f} nm<br>Absorption: %{y:.1f}%<extra></extra>",
                ),
                secondary_y=True,
            )

    # Add laser overlays
    fig = overlay_lasers(fig, plot_type="tissue")

    # Update layout
    max_y = max(normalized_fraction) * 1.2  # Add 20% padding
    fig.update_layout(
        paper_bgcolor=STYLE_CONFIG["plot_style"]["bgcolor"],
        plot_bgcolor=STYLE_CONFIG["plot_style"]["bgcolor"],
        font=STYLE_CONFIG["plot_style"]["font"],
        margin=dict(
            t=100,  # Increased top margin for title
            r=50,
            b=50,
            l=50
        ),
        xaxis=dict(
            title="Wavelength (nm)",
            range=wavelength_range,  # Keep visible range as specified
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.15)",
            zeroline=False,
        ),
        yaxis=dict(
            title=f"Normalized photon fraction at z={depth} mm",
            range=[0, max_y],
            showgrid=True,
            gridcolor="rgba(128, 128, 128, 0.15)",
            zeroline=False,
        ),
        yaxis2=dict(
            title="Percent photons absorbed",
            range=[0, 100],
            showgrid=False,
            zeroline=False,
        ),
        height=600,
        hovermode="x unified",
        # Add interpretation text in the title
        title=dict(
            text=(
                "Tissue Penetration Plot<br>" +
                "<span style='font-size:0.9em; color:blue'>🔵 Photon Fraction: percentage reaching depth z, normalized at reference wavelength</span><br>" +
                "<span style='font-size:0.9em; color:red'>🔴 Absorption: percentage absorbed, shaded regions >50%</span>"
            ),
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=14),
        )
    )

    return fig

