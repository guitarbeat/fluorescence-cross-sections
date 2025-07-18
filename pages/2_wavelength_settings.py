import streamlit as st

from src.pages.common import render_footer
from src.state.session_state import initialize_session_state

initialize_session_state()

st.header("Wavelength Settings", help="Configure global wavelength parameters")

container = st.container(border=True)
with container:
    st.caption("Configure global wavelength range and normalization settings")
    col1, col2 = st.columns(2)
    with col1:
        wavelength_range = st.slider(
            "Analysis Range (nm)",
            min_value=700,
            max_value=2400,
            value=st.session_state.global_params["wavelength_range"],
            step=10,
            help="Global wavelength range for all plots and analysis",
        )
        st.session_state.global_params["wavelength_range"] = wavelength_range
    with col2:
        norm_wavelength = st.number_input(
            "Normalization λ (nm)",
            min_value=800,
            max_value=2400,
            value=st.session_state.global_params["normalization_wavelength"],
            step=10,
            help="Wavelength at which to normalize the photon fraction",
        )
        st.session_state.global_params["normalization_wavelength"] = norm_wavelength

render_footer()
