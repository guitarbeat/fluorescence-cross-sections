"""Entry point for the Deep Tissue Imaging Optimizer."""
from src.config import DEFAULT_TISSUE_PARAMS
from src.components.dashboard_utils import add_dashboard_css, render_dashboard_metrics
from src.core import initialize_session_state
import streamlit as st
import numpy as np


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    # Add styling
    add_dashboard_css()

    # Initialize data
    initialize_session_state()

    # Metrics cards
    current_depth = st.session_state.tissue_params.get(
        "depth", DEFAULT_TISSUE_PARAMS["depth"])
    current_wavelength = st.session_state.global_params["normalization_wavelength"]
    current_water = st.session_state.tissue_params.get(
        "water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    num_fluorophores = len(
        st.session_state.fluorophore_df) if "fluorophore_df" in st.session_state else 0
    current_g = st.session_state.tissue_params.get(
        "g", DEFAULT_TISSUE_PARAMS["g"])
    current_b = st.session_state.tissue_params.get(
        "b", DEFAULT_TISSUE_PARAMS["b"])
    current_a = st.session_state.tissue_params.get(
        "a", DEFAULT_TISSUE_PARAMS["a"])

    metrics = {
        "depth": {"title": "Depth", "value": f"{current_depth:.1f}mm"},
        "wavelength": {"title": "Wavelength", "value": f"{current_wavelength}nm"},
        "water": {"title": "Water", "value": f"{current_water*100:.0f}%"},
        "anisotropy": {"title": "Anisotropy", "value": f"{current_g:.2f}"},
        "scattering_power": {"title": "Scattering Power", "value": f"{current_b:.2f}"},
        "scattering_scale": {"title": "Scattering Scale", "value": f"{current_a:.2f}"},
        "fluorophores": {"title": "Fluorophores", "value": str(num_fluorophores)},
        "laser": {"title": "Laser", "value": "Config"}
    }
    render_dashboard_metrics(metrics)

    col1, col2 = st.columns(2)

    with col1:
        try:
            from src.components.common import render_plot_container
            render_plot_container(
                "cross_sections", st.session_state.fluorophore_df)
        except Exception as e:
            st.error(f"Error: {e}")

    with col2:
        try:
            from src.components.common import render_plot_container
            render_plot_container("tissue_penetration")
            from src.components.tissue_config import render_scattering_popover, render_absorption_popover, render_transmission_popover
            params = st.session_state.tissue_params
            a = params.get("a", DEFAULT_TISSUE_PARAMS["a"])
            b = params.get("b", DEFAULT_TISSUE_PARAMS["b"])
            g = params.get("g", DEFAULT_TISSUE_PARAMS["g"])
            water_content = params.get(
                "water_content", DEFAULT_TISSUE_PARAMS["water_content"])
            depth = params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
            ref_wavelength = st.session_state.global_params.get(
                "normalization_wavelength", 1300)
            # Compute mus_scattering and mua_lambda for transmission popover
            mus_scattering = a * (ref_wavelength / 500) ** (-b) / (1 - g)
            from src.utils.data_loader import load_water_absorption_data
            water_data = load_water_absorption_data()
            mua_lambda = float(
                np.interp(ref_wavelength, water_data["wavelength"], water_data["absorption"]))
            # Place popovers in a row
            popover_cols = st.columns(3)
            with popover_cols[0]:
                render_scattering_popover(a, g, b, ref_wavelength)
            with popover_cols[1]:
                render_absorption_popover(water_content, ref_wavelength)
            with popover_cols[2]:
                render_transmission_popover(
                    mus_scattering, mua_lambda, water_content, ref_wavelength, depth)
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
