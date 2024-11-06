from typing import Optional, Dict, Tuple, Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.models.plot_config import get_theme_colors
from ..plots.plot_utils import apply_common_styling
from ..components.laser_manager import overlay_lasers


def create_tissue_plot(
    wavelengths: npt.NDArray[np.float64],
    tissue_data: Dict[str, Any],
    normalization_wavelength: float = 1300,
    depth: float = 1.0,
) -> go.Figure:
    """Create tissue penetration plot with consistent styling."""
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Get theme colors and global parameters
    theme = get_theme_colors()
    absorption_threshold = st.session_state.get("global_absorption_threshold", 50)
    
    # Normalize photon fraction at specified wavelength and depth
    norm_idx = np.abs(wavelengths - normalization_wavelength).argmin()
    norm_factor = tissue_data["T"][norm_idx]
    normalized_fraction = tissue_data["T"] / norm_factor
    
    # Add photon fraction trace
    fig.add_trace(
        go.Scatter(
            x=wavelengths,
            y=normalized_fraction,
            name="Photon Fraction",
            line=dict(color='rgb(0, 0, 255)', width=2),
            showlegend=False,
        ),
        secondary_y=False
    )
    
    # Calculate total attenuation from water absorption data
    absorption_mask = tissue_data["Tw"] * 100 >= absorption_threshold  # Convert to percentage
    
    # Find continuous regions above threshold
    change_points = np.where(np.diff(absorption_mask.astype(int)))[0]
    regions = []
    start_idx = 0
    
    for point in change_points:
        if absorption_mask[start_idx]:  # If region was above threshold
            regions.append((wavelengths[start_idx], wavelengths[point]))
        start_idx = point + 1
    
    # Add final region if it ends above threshold
    if absorption_mask[start_idx:].any():
        regions.append((wavelengths[start_idx], wavelengths[-1]))
    
    # Add shading for each region
    for x0, x1 in regions:
        fig.add_shape(
            type="rect",
            x0=x0,
            x1=x1,
            y0=0,
            y1=100,
            fillcolor="rgba(255, 0, 0, 0.1)",
            line=dict(width=0),
            layer="below",
            yref="y2"
        )
    
    # Add water absorption percentage line with dotted/solid segments
    i = 0
    absorption = tissue_data["Tw"] * 100  # Convert to percentage
    
    while i < len(wavelengths)-1:
        # Find segments of continuous above/below threshold
        start_idx = i
        is_above_threshold = absorption[i] >= absorption_threshold
        
        while (i < len(wavelengths)-1 and 
               (absorption[i+1] >= absorption_threshold) == is_above_threshold):
            i += 1
        
        # Add segment
        fig.add_trace(
            go.Scatter(
                x=wavelengths[start_idx:i+1],
                y=absorption[start_idx:i+1],
                mode='lines',
                line=dict(
                    color='rgb(255, 0, 0)',
                    width=2,
                    dash='solid' if is_above_threshold else 'dot'
                ),
                showlegend=False,
                name="Water Absorption",
            ),
            secondary_y=True
        )
        i += 1

    # Add laser overlays
    fig = overlay_lasers(fig, plot_type="tissue")
    
    # Apply common styling with updated title
    apply_common_styling(
        fig,
        title=f"Photon Fraction (normalized at {normalization_wavelength} nm, depth={depth} mm)",
        yaxis_title="Normalized photon fraction",
        xaxis_range=(wavelengths[0], wavelengths[-1])
    )
    
    # Update secondary y-axis
    fig.update_yaxes(
        title_text="Water Absorption (%)",
        secondary_y=True,
        range=[0, 100]
    )

    return fig
