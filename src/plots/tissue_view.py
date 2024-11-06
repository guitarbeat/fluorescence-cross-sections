import numpy as np
import streamlit as st

from src.models.tissue_config import DEFAULT_TISSUE_PARAMS, TISSUE_FORMULA_CONFIG
from src.models.tissue_model import calculate_tissue_parameters
from src.plots.tissue_plot import create_tissue_plot


def render_tissue_penetration_view(
    plot_only: bool = False, controls_only: bool = False
):
    """
    Render the tissue penetration view with interactive controls.
    """
    if controls_only:
        # Initialize tissue parameters in session state if not present
        st.session_state.setdefault('tissue_params', DEFAULT_TISSUE_PARAMS.copy())

        # Main formula and explanation
        st.latex(TISSUE_FORMULA_CONFIG["main_formula"])
        st.markdown(
            """
            The blue line shows the fraction of photons reaching depth z, normalized at 1300 nm.
            The red line shows the percentage absorbed, with shaded regions indicating >50% absorption.
            """
        )

        # Scattering Parameters Section
        st.markdown("#### Scattering Properties")
        with st.expander("Scattering Coefficient", expanded=True):
            st.latex(TISSUE_FORMULA_CONFIG["additional_formulas"][0]["formula"])
            col1, col2 = st.columns(2)

            with col1:
                g = st.slider(
                    "Anisotropy Factor (g)",
                    0.0,
                    1.0,
                    st.session_state.tissue_params.get("g", 0.9),
                    0.05,
                    help="g=0: Any direction, g=1: Forward only",
                )

                b = st.number_input(
                    "Scattering Power (b)",
                    min_value=0.5,
                    max_value=2.0,
                    value=st.session_state.tissue_params.get("b", 1.37),
                    step=0.05,
                    help="Wavelength dependence (≈1.37 for brain tissue)",
                )

            with col2:
                a_preset_options = {"Low (0.8)": 0.8, "Normal (1.1)": 1.1, "High (1.4)": 1.4}
                a_preset = st.radio(
                    "Scattering Scale (a)",
                    options=list(a_preset_options.keys()),
                    index=1,
                    help="Scattering amplitude [mm⁻¹]",
                )
                a = a_preset_options[a_preset]

        # Absorption Parameters Section
        st.markdown("#### Absorption Properties")
        with st.expander("Absorption Coefficient", expanded=True):
            st.latex(TISSUE_FORMULA_CONFIG["additional_formulas"][1]["formula"])
            st.markdown(
                """
                In brain tissue, water is the primary absorber at higher wavelengths:
                - No fat or pigment present
                - Hemoglobin doesn't absorb at higher wavelengths
                - Major water absorption peaks at 1450 nm and 1950 nm
                """
            )

            water_content = st.select_slider(
                "Water Content",
                options=[i / 100 for i in range(0, 105, 5)],
                value=st.session_state.tissue_params.get("water_content", 0.75),
                help="Fraction of tissue that is water (≈75% for brain)",
            )

        # Add absorption threshold control
        st.markdown("#### Absorption Settings")
        absorption_threshold = st.slider(
            "Absorption Threshold (%)",
            min_value=0,
            max_value=100,
            value=st.session_state.tissue_params.get("absorption_threshold", 50),
            help="Threshold for absorption shading (regions above this value will be shaded)",
        )
        
        # Update session state
        st.session_state.tissue_params.update({
            "water_content": water_content,
            "g": g,
            "a": a,
            "b": b,
            "absorption_threshold": absorption_threshold,
        })
        return

    # Use global parameters for calculations
    wavelength_range = st.session_state.get("global_wavelength_range", (800, 2400))
    wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], 1000)
    
    # Get global parameters
    depth = st.session_state.get("global_depth", 1.0)
    norm_wavelength = st.session_state.get("global_norm_wavelength", 1300)
    
    # Calculate parameters for plot
    tissue_params = st.session_state.get("tissue_params", DEFAULT_TISSUE_PARAMS.copy())
    
    # Use global parameters for calculation
    calculation_params = {
        "g": tissue_params["g"],
        "a": tissue_params["a"],
        "water_content": tissue_params["water_content"],
        "b": tissue_params["b"],
        "depth": depth,  # Use global depth
        "normalization_wavelength": norm_wavelength,  # Use global normalization wavelength
    }
    
    # Calculate tissue parameters
    tissue_data = calculate_tissue_parameters(wavelengths, **calculation_params)

    # Create and return plot with threshold
    fig = create_tissue_plot(
        wavelengths=wavelengths,
        tissue_data={
            "photon_fraction": tissue_data["T"],
            "absorption": tissue_data["Tw"] * 100,
            "two_photon_data": tissue_data.get("two_photon_data"),
        },
        normalization_wavelength=norm_wavelength,
        absorption_threshold=st.session_state.tissue_params.get("absorption_threshold", 50)
    )

    if plot_only:
        return fig

    # Display plot with custom theme
    st.plotly_chart(fig, use_container_width=True, theme=None)
