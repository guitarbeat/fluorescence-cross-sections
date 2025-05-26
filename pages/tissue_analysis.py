"""Tissue Penetration Analysis Page"""
import streamlit as st
import numpy as np
from src.plots.tissue_view import calculate_tissue_parameters, create_tissue_plot
from src.config.tissue_config import render_math_view


@st.cache_data(ttl=300)  # Cache for 5 minutes
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


# Main tissue penetration analysis page
st.header("🔬 Tissue Penetration Analysis")
st.caption("Analyze tissue penetration characteristics and parameters")

# Get parameters from session state
global_params = st.session_state.global_params
tissue_params = st.session_state.tissue_params
depth = tissue_params.get("depth", 1.0)
norm_wavelength = global_params["normalization_wavelength"]
wavelength_range = global_params["wavelength_range"]
absorption_threshold = global_params["absorption_threshold"]

# Direct container with border for better visual separation
plot_container = st.container(border=True)
with plot_container:
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

    # Set fixed square size
    PLOT_SIZE = 800
    fig.update_layout(
        width=PLOT_SIZE,
        height=PLOT_SIZE,
        autosize=False,
    )

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

# Render mathematical formulas and additional information
render_math_view()
