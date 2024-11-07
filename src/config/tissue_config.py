"""Configuration for tissue penetration modeling."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# Changed from relative to absolute import
from src.utils.data_loader import load_water_absorption_data

# Formula display configuration
MAIN_FORMULA_SIZE = r"\huge"  # Size for the main formula
FORMULA_SIZE = r"\large"      # Size for other formulas
FORMULA_SPACING = 2          # Number of blank lines after formulas

# Plot configuration
PLOT_CONFIG = {
    "height": 300,
    "small_height": 250,  # Increased height for parameter plots
    "margin": dict(l=20, r=20, t=40, b=20),  # Adjusted margins
    "small_margin": dict(l=20, r=20, t=40, b=20),
    "hovermode": 'x unified',
    "wavelength_range": [800, 2400],
    "reference_wavelength": 1300,
    "showlegend": False,  # Hide legend by default
    "aspect_ratio": 1.2,  # For more square-like appearance
}

# Default tissue parameters to match the paper
DEFAULT_TISSUE_PARAMS = {
    "depth": 1.0,  # 1mm depth as shown in image
    "water_content": 0.75,  # 75% as specified
    "g": 0.9,  # Matches paper
    "a": 1.1,  # 1.1 mm^-1 as specified
    "b": 1.37,  # Matches paper
    "absorption_threshold": 50,  # Percentage threshold for shading
}


def create_coefficient_plot(
    wavelengths: np.ndarray,
    y_values: np.ndarray,
    title: str,
    line_color: str,
    marker_color: str,
) -> go.Figure:
    """Create a coefficient plot with consistent styling."""
    fig = go.Figure()

    # Add main line
    fig.add_trace(go.Scatter(
        x=wavelengths,
        y=y_values,
        mode='lines',
        showlegend=False,
        line=dict(color=line_color)
    ))

    # Add reference point
    ref_idx = np.abs(
        wavelengths - PLOT_CONFIG["reference_wavelength"]).argmin()
    fig.add_trace(go.Scatter(
        x=[PLOT_CONFIG["reference_wavelength"]],
        y=[y_values[ref_idx]],
        mode='markers',
        showlegend=False,
        marker=dict(size=10, color=marker_color)
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Wavelength (nm)",
        yaxis_title=f"{title} (mm⁻¹)",
        height=PLOT_CONFIG["height"],
        margin=PLOT_CONFIG["margin"],
        hovermode=PLOT_CONFIG["hovermode"],
        showlegend=False
    )

    return fig


def add_formula_spacing():
    """Add consistent spacing after formulas."""
    for _ in range(FORMULA_SPACING):
        st.write("")


def create_parameter_relationship_plot(
    param_values: np.ndarray,
    coefficients: np.ndarray,
    param_name: str,
    current_value: float,
    line_color: str,
) -> go.Figure:
    """Create a plot showing direct relationship between parameter and coefficient."""
    fig = go.Figure()

    # Add main line
    fig.add_trace(go.Scatter(
        x=param_values,
        y=coefficients,
        mode='lines',
        showlegend=False,  # Hide legend
        line=dict(color=line_color)
    ))

    # Add point for current value
    fig.add_trace(go.Scatter(
        x=[current_value],
        y=[np.interp(current_value, param_values, coefficients)],
        mode='markers',
        showlegend=False,  # Hide legend
        marker=dict(size=10, color='black')
    ))

    # Update layout for more square-like appearance
    fig.update_layout(
        title=dict(
            text=f"Coefficient vs {param_name}",
            y=0.95,  # Adjust title position
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        xaxis_title=param_name,
        yaxis_title="Coefficient (mm⁻¹)",
        height=PLOT_CONFIG["small_height"],
        margin=PLOT_CONFIG["small_margin"],
        hovermode='x unified',
        showlegend=False,
        # Make plot more square-like
        width=PLOT_CONFIG["small_height"] * PLOT_CONFIG["aspect_ratio"]
    )

    return fig


def render_scattering_section(col, params) -> tuple[float, float, float]:
    """
    Render the scattering properties section.

    Args:
        col: Streamlit column object
        params: Dictionary of tissue parameters

    Returns:
        tuple[float, float, float]: Updated (g, b, a) parameters
    """

    # Create two columns for plot and controls
    plot_col, controls_col = col.columns([2, 1])

    with plot_col:
        # Main scattering plot
        wavelengths = np.linspace(*PLOT_CONFIG["wavelength_range"], 1000)
        mus_prime = params['a'] * (wavelengths / 500) ** (-params['b'])
        mus = mus_prime / (1 - params['g'])

        fig = create_coefficient_plot(
            wavelengths=wavelengths,
            y_values=mus,
            title="Scattering Coefficient",
            line_color='blue',
            marker_color='red'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Scattering formula below the plot
        st.markdown("#### Scattering Formula")
        scattering_formula = (
            f"{FORMULA_SIZE} \\mu_s(\\lambda) = \\frac{{a}}{{1-g}} \\cdot "
            r"\left(\frac{\lambda}{500}\right)^{-b} "
            f"\\quad = \\frac{{\\color{{red}}{{{params['a']:.2f}}}}}"
            f"{{1-\\color{{red}}{{{params['g']:.2f}}}}} \\cdot "
            r"\left(\frac{\lambda}{500}\right)^{" +
            f"\\color{{red}}{{-{params['b']:.2f}}}" + "}"
        )
        st.latex(scattering_formula)

    with controls_col:
        st.markdown("### Parameter Controls")

        # Column 1: Anisotropy
        g = st.slider(
            "Anisotropy (g)",
            0.0, 1.0, params["g"], 0.05,
            help="Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
        )

        with st.expander("📊 Anisotropy Impact"):
            g_values = np.linspace(0.1, 0.99, 100)
            mus_g = params['a'] / (1 - g_values)

            g_fig = create_parameter_relationship_plot(
                param_values=g_values,
                coefficients=mus_g,
                param_name="Anisotropy",
                current_value=g,
                line_color='blue'
            )
            st.plotly_chart(g_fig, use_container_width=True)
            st.markdown("""
                **Impact of Anisotropy:**
                - Higher values → more forward scattering
                - Lower values → more uniform scattering
                - Brain tissue typically ≈ 0.9
                
                *g represents the average cosine of the scattering angle*
            """)

        # Column 2: Scattering power (b)
        b = st.number_input(
            "Scattering Power (b)",
            min_value=0.5,
            max_value=2.0,
            value=params["b"],
            step=0.05,
            help="Wavelength dependence (≈1.37 for brain tissue)",
        )

        with st.expander("📈 Wavelength Dependence Impact"):
            b_values = np.linspace(0.5, 2.0, 100)
            ref_wavelength = PLOT_CONFIG["reference_wavelength"]
            mus_b = params['a'] * (ref_wavelength /
                                   500) ** (-b_values) / (1 - params['g'])

            b_fig = create_parameter_relationship_plot(
                param_values=b_values,
                coefficients=mus_b,
                param_name="Scattering Power (b)",
                current_value=b,
                line_color='blue'
            )
            st.plotly_chart(b_fig, use_container_width=True)
            st.markdown("""
                **Impact of Scattering Power:**
                - Controls wavelength dependence
                - Higher b → stronger λ dependence
                - Brain tissue b ≈ 1.37
            """)

        # Column 3: Scattering scale (a)
        a = st.number_input(
            "Scattering Scale (a)",
            min_value=0.5,
            max_value=2.0,
            value=params["a"],
            step=0.1,
            help="Scattering amplitude [mm⁻¹]",
        )

        with st.expander("📉 Scattering Amplitude Impact"):
            a_values = np.linspace(0.5, 2.0, 100)
            mus_a = a_values * \
                (PLOT_CONFIG["reference_wavelength"] /
                 500) ** (-params['b']) / (1 - params['g'])

            a_fig = create_parameter_relationship_plot(
                param_values=a_values,
                coefficients=mus_a,
                param_name="Scattering Scale (a)",
                current_value=a,
                line_color='blue'
            )
            st.plotly_chart(a_fig, use_container_width=True)
            st.markdown("""
                **Impact of Scattering Scale:**
                - Controls overall scattering strength
                - Higher a → more scattering
                - Brain tissue a ≈ 1.1 mm⁻¹
            """)

    return g, b, a


def render_absorption_section(col, params) -> float:
    """
    Render the absorption properties section.

    Args:
        col: Streamlit column object
        params: Dictionary of tissue parameters

    Returns:
        float: Updated water_content parameter
    """

    # Create two columns for plot and controls
    plot_col, controls_col = col.columns([2, 1])

    with plot_col:
        # Main absorption plot
        water_data = load_water_absorption_data()
        wavelengths = np.linspace(*PLOT_CONFIG["wavelength_range"], 1000)
        mua = np.interp(
            wavelengths, water_data["wavelength"], water_data["absorption"])
        mua = mua * params['water_content'] / 10

        fig = create_coefficient_plot(
            wavelengths=wavelengths,
            y_values=mua,
            title="Absorption Coefficient",
            line_color='red',
            marker_color='blue'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Absorption formula below the plot
        st.markdown("#### Absorption Formula")
        absorption_formula = (
            f"{FORMULA_SIZE} \\mu_a(\\lambda) = \\mu_{{a,base}} \\cdot w "
            f"\\quad = \\mu_{{a,base}} \\cdot \\color{{red}}{{{
                params['water_content']:.2f}}}"
        )
        st.latex(absorption_formula)

    with controls_col:
        st.markdown("### Parameter Controls")

        # Water content control
        water_content = st.select_slider(
            "Water Content",
            options=[i / 100 for i in range(0, 105, 5)],
            value=params["water_content"],
            help="Fraction of tissue that is water (≈75% for brain)",
        )

        with st.expander("💧 Water Content Impact"):
            w_values = np.linspace(0, 1, 100)
            water_data = load_water_absorption_data()
            ref_wavelength = PLOT_CONFIG["reference_wavelength"]
            base_absorption = np.interp(
                ref_wavelength, water_data["wavelength"], water_data["absorption"]) / 10
            mua_w = base_absorption * w_values

            w_fig = create_parameter_relationship_plot(
                param_values=w_values,
                coefficients=mua_w,
                param_name="Water Content",
                current_value=water_content,
                line_color='red'
            )
            st.plotly_chart(w_fig, use_container_width=True)
            st.markdown("""
                **Impact of Water Content:**
                - Controls absorption strength
                - Linear relationship with absorption
                - Brain tissue ≈ 75% water
                - Major peaks at 1450nm and 1950nm
            """)

    return water_content


def render_math_view():
    """Render the tissue penetration controls with improved layout."""
    # Initialize tissue parameters in session state if not present
    st.session_state.setdefault("tissue_params", DEFAULT_TISSUE_PARAMS.copy())
    params = st.session_state.tissue_params

    # Get global parameters
    wavelength_range = st.session_state.global_params.get(
        "wavelength_range", (800, 2400))
    normalization_wavelength = st.session_state.global_params.get(
        "normalization_wavelength", 1300)

    # Update plot config with global settings
    PLOT_CONFIG["wavelength_range"] = wavelength_range
    PLOT_CONFIG["reference_wavelength"] = normalization_wavelength

    # Create main container for the math view
    main_container = st.container()

    with main_container:
        # Header section with main formula and depth control
        header = st.container()
        with header:
            # Title and description in columns
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("### Tissue Penetration Model")
                st.markdown(
                    """
                    This model describes how light penetrates through tissue, accounting for 
                    both scattering and absorption effects.
                    """
                )

            with col2:
                # Depth control in its own column
                depth = params.get("depth", 1.0)
                new_depth = st.slider(
                    "Depth (z) [mm]",
                    min_value=0.1,
                    max_value=2.0,
                    value=depth,
                    step=0.1,
                    help="Distance light travels through tissue",
                )

                if new_depth != depth:
                    st.session_state.tissue_params["depth"] = new_depth
                    st.rerun()

        # Main formula in an expander
        with st.expander("📐 Mathematical Model", expanded=True):
            # Main formula
            main_formula_with_depth = (
                f"{MAIN_FORMULA_SIZE} T(\\lambda, z) = "
                f"e^{{-(\\mu_s(\\lambda) + \\mu_a(\\lambda))z}} \\quad = "
                f"e^{{-(\\mu_s(\\lambda) + \\mu_a(\\lambda)) \\cdot "
                f"\\color{{red}}{depth:.1f}}}"
            )
            st.latex(main_formula_with_depth)

            # Description of variables
            st.markdown("""
                where:
                - T(λ,z) is the transmission at wavelength λ and depth z
                - μₛ(λ) is the scattering coefficient
                - μₐ(λ) is the absorption coefficient
            """)
            add_formula_spacing()

        # Results interpretation
        with st.container():
            st.markdown("#### Model Output Interpretation")
            interpretation_col1, interpretation_col2 = st.columns(2)

            with interpretation_col1:
                st.markdown("""
                    🔵 **Photon Fraction**
                    - Shows percentage of photons reaching depth z
                    - Normalized at reference wavelength
                """)

            with interpretation_col2:
                st.markdown("""
                    🔴 **Absorption**
                    - Shows percentage of photons absorbed
                    - Shaded regions indicate >50% absorption
                """)

        # Parameters section with tabs
        param_tabs = st.tabs(
            ["Scattering Properties", "Absorption Properties"])

        # Initialize variables with default values
        g, b, a = params["g"], params["b"], params["a"]
        water_content = params["water_content"]

        try:
            with param_tabs[0]:
                # Scattering parameters
                scattering_result = render_scattering_section(st, params)
                if scattering_result is not None:
                    g, b, a = scattering_result

            with param_tabs[1]:
                # Absorption parameters
                absorption_result = render_absorption_section(st, params)
                if absorption_result is not None:
                    water_content = absorption_result

            # Update session state only if we got valid results
            st.session_state.tissue_params.update({
                "water_content": water_content,
                "g": g,
                "a": a,
                "b": b,
                "depth": depth,
            })

        except (ValueError, TypeError, AttributeError) as e:
            st.error(f"Error updating parameters: {str(e)}")
