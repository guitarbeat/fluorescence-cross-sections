import streamlit as st

from src.config.tissue_config import DEFAULT_TISSUE_PARAMS
from src.state.session_state import initialize_session_state
from src.pages.common import render_footer
from src.config.constants import TISSUE_DEPTH_SLIDER_CONFIG

initialize_session_state()

st.header("Tissue Parameters", help="Configure tissue-specific parameters")

general_tab, absorption_tab, scattering_tab = st.tabs([
    "🔬 General Settings",
    "💧 Absorption Properties",
    "🌊 Scattering Properties",
])

with general_tab:
    st.caption("Configure general tissue analysis parameters")
    col1, col2 = st.columns(2)
    with col1:
        depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
        new_depth = st.slider(
            "Tissue Depth (mm)",
            value=depth,
            key="tissue_depth_main",
            **TISSUE_DEPTH_SLIDER_CONFIG,
        )
        if new_depth != depth:
            st.session_state.tissue_params["depth"] = new_depth
    with col2:
        absorption_threshold = st.slider(
            "Absorption Threshold (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.global_params["absorption_threshold"],
            help="Threshold for absorption shading",
        )
        st.session_state.global_params["absorption_threshold"] = absorption_threshold

with absorption_tab:
    st.caption("Configure water content and absorption properties")
    water_content = st.select_slider(
        "Water Content",
        options=[i / 100 for i in range(0, 105, 5)],
        value=st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"]),
        help="Fraction of tissue that is water (≈75% for brain)",
        key="absorption_water_content",
    )
    st.session_state.tissue_params["water_content"] = water_content
    st.info(
        """**Water Absorption Properties:**\n- Controls absorption strength linearly\n- Brain tissue ≈ 75% water\n- Major absorption peaks at 1450nm and 1950nm\n- Formula: μₐ(λ) = μₐᵏ(λ) × water_content"""
    )

with scattering_tab:
    st.caption("Configure anisotropy, scattering power, and amplitude")
    col1, col2, col3 = st.columns(3)
    with col1:
        g = st.slider(
            "Anisotropy (g)",
            0.0,
            1.0,
            st.session_state.tissue_params.get("g", DEFAULT_TISSUE_PARAMS["g"]),
            0.05,
            help="Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
            key="scattering_anisotropy",
        )
        st.session_state.tissue_params["g"] = g
    with col2:
        b = st.number_input(
            "Scattering Power (b)",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.tissue_params.get("b", DEFAULT_TISSUE_PARAMS["b"]),
            step=0.05,
            help="Wavelength dependence (≈1.37 for brain tissue)",
            key="scattering_power",
        )
        st.session_state.tissue_params["b"] = b
    with col3:
        a = st.number_input(
            "Scattering Scale (a)",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.tissue_params.get("a", DEFAULT_TISSUE_PARAMS["a"]),
            step=0.1,
            help="Scattering amplitude [mm⁻¹]",
            key="scattering_scale",
        )
        st.session_state.tissue_params["a"] = a
    st.info(
        """**Light Scattering Properties:**\n- **Anisotropy (g)**: Controls scattering direction (brain ≈ 0.9)\n- **Power (b)**: Wavelength dependence (brain ≈ 1.37)\n- **Scale (a)**: Overall scattering strength (brain ≈ 1.1 mm⁻¹)\n- Formula: μₛ(λ) = a/(1-g) × (λ/500)⁻ᵇ"""
    )

render_footer()
