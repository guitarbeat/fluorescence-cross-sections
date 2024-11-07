"""Configuration for tissue penetration modeling."""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from ..utils.data_loader import load_water_absorption_data

# Formula display configuration
MAIN_FORMULA_SIZE = r"\huge"  # Size for the main formula
FORMULA_SIZE = r"\large"      # Size for other formulas
FORMULA_SPACING = 2          # Number of blank lines after formulas

# Plot configuration
PLOT_CONFIG = {
    "height": 300,
    "small_height": 150,  # Height for parameter effect plots
    "margin": dict(l=0, r=0, t=30, b=0),
    "small_margin": dict(l=0, r=0, t=20, b=0),  # Tighter margins for small plots
    "hovermode": 'x unified',
    "wavelength_range": [800, 2400],
    "reference_wavelength": 1300,
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
    ref_value: float,
) -> go.Figure:
    """Create a coefficient plot with consistent styling."""
    fig = go.Figure()
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=wavelengths,
        y=y_values,
        mode='lines',
        name=title,
        line=dict(color=line_color)
    ))
    
    # Add reference point
    ref_idx = np.abs(wavelengths - PLOT_CONFIG["reference_wavelength"]).argmin()
    fig.add_trace(go.Scatter(
        x=[PLOT_CONFIG["reference_wavelength"]],
        y=[y_values[ref_idx]],
        mode='markers',
        name=f'Value at {PLOT_CONFIG["reference_wavelength"]}nm: {y_values[ref_idx]:.2f}',
        marker=dict(size=10, color=marker_color)
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Wavelength (nm)",
        yaxis_title=f"{title} (mm⁻¹)",
        height=PLOT_CONFIG["height"],
        margin=PLOT_CONFIG["margin"],
        hovermode=PLOT_CONFIG["hovermode"]
    )
    
    return fig

def add_formula_spacing():
    """Add consistent spacing after formulas."""
    for _ in range(FORMULA_SPACING):
        st.write("")

def create_parameter_effect_plot(
    wavelengths: np.ndarray,
    y_values_list: list[np.ndarray],
    param_values: list[float],
    title: str,
    line_color: str,
) -> go.Figure:
    """Create a plot showing the effect of a parameter."""
    fig = go.Figure()
    
    # Calculate color with different transparencies
    base_color = line_color
    alphas = np.linspace(0.3, 1.0, len(param_values))
    
    for y_values, param_value, alpha in zip(y_values_list, param_values, alphas):
        # Convert color to rgba
        if base_color == 'blue':
            rgba_color = f'rgba(0, 0, 255, {alpha})'
        elif base_color == 'red':
            rgba_color = f'rgba(255, 0, 0, {alpha})'
        
        fig.add_trace(go.Scatter(
            x=wavelengths,
            y=y_values,
            mode='lines',
            name=f'{param_value:.2f}',
            line=dict(color=rgba_color, width=2)
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Wavelength (nm)",
        yaxis_title="Coefficient (mm⁻¹)",
        height=PLOT_CONFIG["small_height"],
        margin=PLOT_CONFIG["small_margin"],
        hovermode=PLOT_CONFIG["hovermode"],
        showlegend=True,
        legend_title="Parameter Value"
    )
    
    return fig

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
        name='Coefficient',
        line=dict(color=line_color)
    ))
    
    # Add point for current value
    fig.add_trace(go.Scatter(
        x=[current_value],
        y=[np.interp(current_value, param_values, coefficients)],
        mode='markers',
        name='Current Value',
        marker=dict(size=10, color='black')
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Coefficient vs {param_name}",
        xaxis_title=param_name,
        yaxis_title="Coefficient (mm⁻¹)",
        height=PLOT_CONFIG["small_height"],
        margin=PLOT_CONFIG["small_margin"],
        hovermode='x unified'
    )
    
    return fig

def render_scattering_section(col, params):
    """Render the scattering properties section."""
    # Get normalization wavelength from global params
    normalization_wavelength = st.session_state.global_params.get("normalization_wavelength", 1300)
    
    # Update reference wavelength in plots
    ref_wavelength = normalization_wavelength
    
    # Main scattering plot
    wavelengths = np.linspace(*PLOT_CONFIG["wavelength_range"], 1000)
    mus_prime = params['a'] * (wavelengths / 500) ** (-params['b'])
    mus = mus_prime / (1 - params['g'])
    
    fig = create_coefficient_plot(
        wavelengths=wavelengths,
        y_values=mus,
        title="Scattering Coefficient",
        line_color='blue',
        marker_color='red',
        ref_value=mus[np.abs(wavelengths - ref_wavelength).argmin()]
    )
    col.plotly_chart(fig, use_container_width=True)
    add_formula_spacing()
    # Formula with current values
    scattering_formula = (
        f"{FORMULA_SIZE} \\mu_s(\\lambda) = \\frac{{a}}{{1-g}} \\cdot "
        r"\left(\frac{\lambda}{500}\right)^{-b} "
        f"\\quad = \\frac{{\\color{{red}}{{{params['a']:.2f}}}}}"
        f"{{1-\\color{{red}}{{{params['g']:.2f}}}}} \\cdot "
        r"\left(\frac{\lambda}{500}\right)^{" + 
        f"\\color{{red}}{{-{params['b']:.2f}}}" + "}"
    )
    col.latex(scattering_formula)
    add_formula_spacing()
    # Parameter controls with relationship plots in 3 columns
    col.markdown("##### Parameter Controls")
    param_col1, param_col2, param_col3 = col.columns(3)
    
    # Column 1: Anisotropy factor (g)
    with param_col1:
        g = st.slider(
            "Anisotropy Factor (g)",
            0.0, 1.0, params["g"], 0.05,
            help="g=0: Any direction, g=1: Forward only",
        )
        
        with st.popover("Show g relationship"):
            g_values = np.linspace(0.1, 0.99, 100)  # Avoid g=1 which gives infinity
            mus_g = params['a'] / (1 - g_values)  # Simplified relationship at reference wavelength
            
            g_fig = create_parameter_relationship_plot(
                param_values=g_values,
                coefficients=mus_g,
                param_name="Anisotropy (g)",
                current_value=g,
                line_color='blue'
            )
            st.plotly_chart(g_fig, use_container_width=True)

    # Column 2: Scattering power (b)
    with param_col2:
        b = st.number_input(
            "Scattering Power (b)",
            min_value=0.5,
            max_value=2.0,
            value=params["b"],
            step=0.05,
            help="Wavelength dependence (≈1.37 for brain tissue)",
        )
        
        with st.popover("Show b relationship"):
            b_values = np.linspace(0.5, 2.0, 100)
            ref_wavelength = PLOT_CONFIG["reference_wavelength"]
            mus_b = params['a'] * (ref_wavelength / 500) ** (-b_values) / (1 - params['g'])
            
            b_fig = create_parameter_relationship_plot(
                param_values=b_values,
                coefficients=mus_b,
                param_name="Scattering Power (b)",
                current_value=b,
                line_color='blue'
            )
            st.plotly_chart(b_fig, use_container_width=True)

    # Column 3: Scattering scale (a)
    with param_col3:
        a = st.number_input(
            "Scattering Scale (a)",
            min_value=0.5,
            max_value=2.0,
            value=params["a"],
            step=0.1,
            help="Scattering amplitude [mm⁻¹]",
        )
        
        with st.popover("Show a relationship"):
            a_values = np.linspace(0.5, 2.0, 100)
            mus_a = a_values * (PLOT_CONFIG["reference_wavelength"] / 500) ** (-params['b']) / (1 - params['g'])
            
            a_fig = create_parameter_relationship_plot(
                param_values=a_values,
                coefficients=mus_a,
                param_name="Scattering Scale (a)",
                current_value=a,
                line_color='blue'
            )
            st.plotly_chart(a_fig, use_container_width=True)
    
    return g, b, a

def render_absorption_section(col, params):
    """Render the absorption properties section."""
    # Get normalization wavelength from global params
    normalization_wavelength = st.session_state.global_params.get("normalization_wavelength", 1300)
    
    # Update reference wavelength in plots
    ref_wavelength = normalization_wavelength
    
    # Main absorption plot
    water_data = load_water_absorption_data()
    wavelengths = np.linspace(*PLOT_CONFIG["wavelength_range"], 1000)
    mua = np.interp(wavelengths, water_data["wavelength"], water_data["absorption"])
    mua = mua * params['water_content'] / 10  # Scale by water content and convert units
    
    fig = create_coefficient_plot(
        wavelengths=wavelengths,
        y_values=mua,
        title="Absorption Coefficient",
        line_color='red',
        marker_color='blue',
        ref_value=mua[np.abs(wavelengths - ref_wavelength).argmin()]
    )
    col.plotly_chart(fig, use_container_width=True)
    add_formula_spacing()

    # Formula with current value
    absorption_formula = (
        f"{FORMULA_SIZE} \\mu_a(\\lambda) = \\mu_{{a,base}} \\cdot w "
        f"\\quad = \\mu_{{a,base}} \\cdot \\color{{red}}{{{params['water_content']:.2f}}}"
    )
    col.latex(absorption_formula)
    add_formula_spacing()


    col.markdown("##### Parameter Controls")
    col.markdown(
        """
        In brain tissue, water is the primary absorber at higher wavelengths:
        - No fat or pigment present
        - Hemoglobin doesn't absorb at higher wavelengths
        - Major water absorption peaks at 1450 nm and 1950 nm
        """
    )

    # Water content control and relationship plot
    water_content = col.select_slider(
        "Water Content",
        options=[i / 100 for i in range(0, 105, 5)],
        value=params["water_content"],
        help="Fraction of tissue that is water (≈75% for brain)",
    )
    
    with col.popover("Show water content relationship"):
        w_values = np.linspace(0, 1, 100)
        water_data = load_water_absorption_data()
        ref_wavelength = PLOT_CONFIG["reference_wavelength"]
        base_absorption = np.interp(ref_wavelength, water_data["wavelength"], water_data["absorption"]) / 10
        mua_w = base_absorption * w_values
        
        w_fig = create_parameter_relationship_plot(
            param_values=w_values,
            coefficients=mua_w,
            param_name="Water Content",
            current_value=water_content,
            line_color='red'
        )
        st.plotly_chart(w_fig, use_container_width=True)
    
    return water_content

def render_math_view():
    """Render the tissue penetration controls."""
    # Initialize tissue parameters in session state if not present
    st.session_state.setdefault("tissue_params", DEFAULT_TISSUE_PARAMS.copy())
    params = st.session_state.tissue_params
    
    # Get global parameters
    wavelength_range = st.session_state.global_params.get("wavelength_range", (800, 2400))
    normalization_wavelength = st.session_state.global_params.get("normalization_wavelength", 1300)
    
    # Update plot config with global settings
    PLOT_CONFIG["wavelength_range"] = wavelength_range
    PLOT_CONFIG["reference_wavelength"] = normalization_wavelength  # Update reference wavelength

    # Main formula and explanation with depth parameter
    depth = params.get("depth", 1.0)
    main_formula_with_depth = (
        f"{MAIN_FORMULA_SIZE} T(\\lambda, z) = e^{{-(\\mu_s(\\lambda) + \\mu_a(\\lambda))z}} "
        f"\\quad = e^{{-(\\mu_s(\\lambda) + \\mu_a(\\lambda)) \\cdot \\color{{red}}{depth:.1f}}}"
    )
    st.latex(main_formula_with_depth)
    add_formula_spacing()
    
    # Add depth slider at the top level
    new_depth = st.slider(
        "Depth (z) [mm]",
        min_value=0.1,
        max_value=2.0,
        value=depth,
        step=0.1,
        help="Distance light travels through tissue",
    )

    # Update depth in session state if changed
    if new_depth != depth:
        st.session_state.tissue_params["depth"] = new_depth
        # Force rerun to update all plots
        st.rerun()

    st.markdown(
        """
        The blue line shows the fraction of photons reaching depth z, normalized at 1300 nm.
        The red line shows the percentage absorbed, with shaded regions indicating >50% absorption.
        """
    )
    add_formula_spacing()

    # Create two columns for scattering and absorption
    scattering_col, divider_col, absorption_col = st.columns([10, 1, 10])

    # Render sections
    g, b, a = render_scattering_section(scattering_col, params)
    
    # Vertical divider
    with divider_col:
        st.markdown(
            """
            <div style="width: 100%; height: 100%; border-left: 2px solid #E0E0E0;"></div>
            """,
            unsafe_allow_html=True
        )
    
    water_content = render_absorption_section(absorption_col, params)

    # Update session state
    st.session_state.tissue_params.update(
        {
            "water_content": water_content,
            "g": g,
            "a": a,
            "b": b,
            "depth": depth,
        }
    )
