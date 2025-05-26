"""Tissue Parameters Page"""
import streamlit as st
from src.config.tissue_config import DEFAULT_TISSUE_PARAMS

# Main tissue parameters page
st.header("🔬 Tissue Parameters")
st.caption("Configure tissue-specific parameters for analysis")

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
