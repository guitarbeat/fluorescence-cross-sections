"""Dashboard utilities for consistent styling and layout."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional


def render_apply_cancel_buttons(apply_label="Apply", cancel_label="Cancel", on_apply=None, on_cancel=None):
    """Render a row of Apply/Cancel buttons with optional callbacks."""
    col1, col2 = st.columns(2)
    with col1:
        if st.button(apply_label, type="primary", use_container_width=True):
            if on_apply:
                on_apply()
    with col2:
        if st.button(cancel_label, use_container_width=True):
            if on_cancel:
                on_cancel()


def render_close_button(label="Close"):
    st.divider()
    if st.button(label, use_container_width=True):
        st.rerun()


@st.dialog("Edit Depth")
def edit_depth_dialog():
    """Dialog for editing tissue depth."""
    from fluorescence.config import DEFAULT_TISSUE_PARAMS

    current_depth = st.session_state.tissue_params.get(
        "depth", DEFAULT_TISSUE_PARAMS["depth"])

    st.write("Adjust the tissue penetration depth:")

    new_depth = st.slider(
        "Depth (mm)",
        min_value=0.1,
        max_value=5.0,
        value=current_depth,
        step=0.1,
        help="Tissue penetration depth for analysis"
    )

    def apply():
        st.session_state.tissue_params["depth"] = new_depth
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


@st.dialog("Wavelength Settings", width="large")
def edit_wavelength_dialog():
    """Dialog for editing wavelength parameters."""
    current_wavelength = st.session_state.global_params["normalization_wavelength"]
    current_range = st.session_state.global_params["wavelength_range"]

    st.write("Configure wavelength analysis parameters:")

    # Create two columns for the parameters
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Analysis Range")
        new_range = st.select_slider(
            "Wavelength Range (nm)",
            options=list(range(700, 1701, 50)),
            value=current_range,
            help="Wavelength range for analysis and plotting"
        )

        # Show range info
        st.info(f"Analysis will cover {new_range[0]} - {new_range[1]} nm")

    with col2:
        st.subheader("🎯 Normalization")
        new_wavelength = st.number_input(
            "Normalization Wavelength (nm)",
            value=current_wavelength,
            min_value=700,
            max_value=1600,
            step=10,
            help="Wavelength used for normalization calculations"
        )

        # Validation
        if new_wavelength < new_range[0] or new_wavelength > new_range[1]:
            st.warning(
                "⚠️ Normalization wavelength should be within the analysis range")

    st.divider()

    def apply():
        st.session_state.global_params["normalization_wavelength"] = new_wavelength
        st.session_state.global_params["wavelength_range"] = new_range
        st.success("Wavelength settings updated!")
        st.rerun()
    render_apply_cancel_buttons(
        apply_label="Apply Changes", on_apply=apply, on_cancel=st.rerun)


@st.dialog("Edit Water Content")
def edit_water_dialog():
    """Dialog for editing tissue water content."""
    from fluorescence.config import DEFAULT_TISSUE_PARAMS

    current_water = st.session_state.tissue_params.get(
        "water_content", DEFAULT_TISSUE_PARAMS["water_content"])
    if isinstance(current_water, float):
        current_water_percent = int(current_water * 100)
    else:
        current_water_percent = current_water

    st.write("Adjust the tissue water content:")

    new_water_percent = st.select_slider(
        "Water Content (%)",
        options=[40, 50, 60, 70, 75, 80, 90],
        value=current_water_percent,
        help="Percentage of water content in tissue"
    )

    def apply():
        st.session_state.tissue_params["water_content"] = new_water_percent / 100
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


@st.dialog("Laser Configuration", width="large")
def edit_laser_dialog():
    """Dialog for laser configuration."""
    st.write("Configure laser settings:")

    try:
        from fluorescence.components.laser_manager import render_laser_manager
        render_laser_manager()
    except Exception as e:
        st.error(f"Error loading laser configuration: {e}")

    render_close_button()


@st.dialog("Manage Fluorophores", width="large")
def edit_fluorophores_dialog():
    """Dialog for managing fluorophores with cross-section data."""
    st.write("View cross-section data and manage your fluorophore selection:")

    # Create tabs for different views - Manage Selection first
    tab1, tab2, tab3 = st.tabs(
        ["✏️ Manage Selection", "📊 Cross-Section Data", "🔍 FPbase Search"])

    with tab1:
        # Show the existing fluorophore data editor
        try:
            from fluorescence.components.common import render_fluorophore_data_editor
            render_fluorophore_data_editor()
        except Exception as e:
            st.error(f"Error loading fluorophore editor: {e}")

    with tab2:
        # Show the fluorophore viewer with cross-section data
        try:
            from fluorescence.utils.data_loader import load_cross_section_data
            from fluorescence.components.fluorophore_viewer import render_fluorophore_viewer

            cross_sections = load_cross_section_data()
            if cross_sections:
                render_fluorophore_viewer(cross_sections, key_prefix="dialog")

                # Add fluorophore to selection
                st.divider()
                selected_fluorophore = st.selectbox(
                    "Add to Analysis",
                    options=[""] + sorted(cross_sections.keys()),
                    help="Select a fluorophore to add to your analysis",
                    key="dialog_add_fluorophore"
                )

                if selected_fluorophore and st.button("Add Fluorophore", type="primary"):
                    # Add the selected fluorophore to the session state
                    if "fluorophore_df" not in st.session_state:
                        st.session_state.fluorophore_df = pd.DataFrame()

                    # Check if fluorophore already exists
                    if not st.session_state.fluorophore_df.empty:
                        existing_names = st.session_state.fluorophore_df.get(
                            'name', pd.Series()).tolist()
                        if selected_fluorophore in existing_names:
                            st.warning(
                                f"{selected_fluorophore} is already in your selection.")
                        else:
                            # Add new fluorophore (simplified - you may need to adjust based on your data structure)
                            new_row = pd.DataFrame({
                                'name': [selected_fluorophore],
                                'visible': [True]
                            })
                            st.session_state.fluorophore_df = pd.concat(
                                [st.session_state.fluorophore_df, new_row], ignore_index=True)
                            st.success(
                                f"Added {selected_fluorophore} to analysis!")
                            st.rerun()
                    else:
                        # First fluorophore
                        st.session_state.fluorophore_df = pd.DataFrame({
                            'name': [selected_fluorophore],
                            'visible': [True]
                        })
                        st.success(
                            f"Added {selected_fluorophore} to analysis!")
                        st.rerun()
            else:
                st.error("Could not load cross-section data.")
        except Exception as e:
            st.error(f"Error loading fluorophore data: {e}")

    with tab3:
        # Show the FPbase search functionality
        try:
            from fluorescence.api.search_form import render_search_panel
            render_search_panel(key_prefix="dialog_search_")
        except Exception as e:
            st.error(f"Error loading FPbase search: {e}")

    # Close button
    st.divider()
    if st.button("Close", use_container_width=True):
        st.rerun()


@st.dialog("Edit Anisotropy (g)")
def edit_anisotropy_dialog():
    """Dialog for editing anisotropy (g) parameter."""
    from fluorescence.config import DEFAULT_TISSUE_PARAMS
    from fluorescence.components.tissue_config import render_parameter_control_with_popover
    import numpy as np

    params = st.session_state.tissue_params
    current_g = params.get("g", DEFAULT_TISSUE_PARAMS["g"])
    a = params.get("a", DEFAULT_TISSUE_PARAMS["a"])

    st.write("Adjust the anisotropy parameter (g):")

    # Use the same popover/slider logic as in tissue_config
    new_g = render_parameter_control_with_popover(
        label="Anisotropy (g)",
        value=current_g,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        help_text="Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
        popover_title="\U0001F4CA Anisotropy Impact",
        popover_help="Click to see how anisotropy affects scattering",
        popover_values=np.linspace(0.1, 0.99, 100),
        popover_coefficients=a / (1 - np.linspace(0.1, 0.99, 100)),
        popover_param_name="Anisotropy",
        popover_current_value=current_g,
        popover_line_color='blue',
        popover_formula=r"\mu_s = \frac{\mu_s'}{1-g} \\ = \frac{a}{1-\color{red}{" +
        f"{current_g:.2f}" + r"}}",
        popover_markdown="""
            - Higher values → more forward scattering
            - Lower values → more uniform scattering
            - Brain tissue typically ≈ 0.9

            *g represents the average cosine of the scattering angle*
        """,
        is_slider=True
    )

    def apply():
        st.session_state.tissue_params["g"] = new_g
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


@st.dialog("Edit Scattering Power (b)")
def edit_scattering_power_dialog():
    """Dialog for editing scattering power (b) parameter."""
    from fluorescence.config import DEFAULT_TISSUE_PARAMS
    from fluorescence.components.tissue_config import render_parameter_control_with_popover
    import numpy as np

    params = st.session_state.tissue_params
    current_b = params.get("b", DEFAULT_TISSUE_PARAMS["b"])
    a = params.get("a", DEFAULT_TISSUE_PARAMS["a"])
    g = params.get("g", DEFAULT_TISSUE_PARAMS["g"])
    ref_wavelength = st.session_state.global_params.get(
        "normalization_wavelength", 1300)

    st.write("Adjust the scattering power (b):")

    new_b = render_parameter_control_with_popover(
        label="Scattering Power (b)",
        value=current_b,
        min_value=0.5,
        max_value=2.0,
        step=0.05,
        help_text="Wavelength dependence (≈1.37 for brain tissue)",
        popover_title="\U0001F4C8 Wavelength Dependence Impact",
        popover_help="Click to see how scattering power affects wavelength dependence",
        popover_values=np.linspace(0.5, 2.0, 100),
        popover_coefficients=a *
        (ref_wavelength / 500) ** (-np.linspace(0.5, 2.0, 100)) / (1 - g),
        popover_param_name="Scattering Power (b)",
        popover_current_value=current_b,
        popover_line_color='blue',
        popover_formula=r"\mu_s' = a \cdot \left(\frac{\lambda}{500}\right)^{-b} \\ = a \cdot \left(\frac{\lambda}{500}\right)^{-\color{red}{" + f"{current_b:.2f}" + r"}}",
        popover_markdown="""
            - Controls wavelength dependence
            - Higher b → stronger λ dependence
            - Brain tissue b ≈ 1.37
        """,
        is_slider=False
    )

    def apply():
        st.session_state.tissue_params["b"] = new_b
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


@st.dialog("Edit Scattering Scale (a)")
def edit_scattering_scale_dialog():
    """Dialog for editing scattering scale (a) parameter."""
    from fluorescence.config import DEFAULT_TISSUE_PARAMS
    from fluorescence.components.tissue_config import render_parameter_control_with_popover
    import numpy as np

    params = st.session_state.tissue_params
    current_a = params.get("a", DEFAULT_TISSUE_PARAMS["a"])
    b = params.get("b", DEFAULT_TISSUE_PARAMS["b"])
    g = params.get("g", DEFAULT_TISSUE_PARAMS["g"])
    ref_wavelength = st.session_state.global_params.get(
        "normalization_wavelength", 1300)

    st.write("Adjust the scattering scale (a):")

    new_a = render_parameter_control_with_popover(
        label="Scattering Scale (a)",
        value=current_a,
        min_value=0.5,
        max_value=2.0,
        step=0.1,
        help_text="Scattering amplitude [mm⁻¹]",
        popover_title="\U0001F4C9 Scattering Amplitude Impact",
        popover_help="Click to see how scattering scale affects overall scattering",
        popover_values=np.linspace(0.5, 2.0, 100),
        popover_coefficients=np.linspace(
            0.5, 2.0, 100) * (ref_wavelength / 500) ** (-b) / (1 - g),
        popover_param_name="Scattering Scale (a)",
        popover_current_value=current_a,
        popover_line_color='blue',
        popover_formula=r"\mu_s = a \cdot \text{(wavelength term)} \\ = \color{red}{" +
        f"{current_a:.2f}" +
        r"}\ \text{mm}^{-1} \cdot \text{(wavelength term)}",
        popover_markdown="""
            - Controls overall scattering strength
            - Higher a → more scattering
            - Brain tissue a ≈ 1.1 mm⁻¹
        """,
        is_slider=False
    )

    def apply():
        st.session_state.tissue_params["a"] = new_a
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


def render_anisotropy_control(current_g: float, a: float) -> float:
    """
    Renders a Streamlit control for the anisotropy parameter (g) and its
    associated scattering coefficient (a).
    """
    from fluorescence.components.tissue_config import render_parameter_control_with_popover
    import numpy as np

    st.write("Adjust the anisotropy parameter (g):")

    new_g = render_parameter_control_with_popover(
        label="Anisotropy (g)",
        value=current_g,
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        help_text="Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
        popover_title="\U0001F4CA Anisotropy Impact",
        popover_help="Click to see how anisotropy affects scattering",
        popover_values=np.linspace(0.1, 0.99, 100),
        popover_coefficients=a / (1 - np.linspace(0.1, 0.99, 100)),
        popover_param_name="Anisotropy",
        popover_current_value=current_g,
        popover_line_color='blue',
        popover_formula=r"\mu_s = \frac{\mu_s'}{1-g} \\ = \frac{a}{1-\color{red}{" +
        f"{current_g:.2f}" + r"}}",
        popover_markdown="""
            - Higher values → more forward scattering
            - Lower values → more uniform scattering
            - Brain tissue typically ≈ 0.9

            *g represents the average cosine of the scattering angle*
        """,
        is_slider=True
    )

    def apply():
        st.session_state.tissue_params["g"] = new_g
        st.rerun()
    render_apply_cancel_buttons(on_apply=apply, on_cancel=st.rerun)


def inject_button_style(key: str, gradient: str):
    """Inject custom CSS for a specific Streamlit button using its key."""
    st.markdown(f"""
    <style>
    div[data-testid="stButton"][data-testid="{key}"] > button {{
        background: {gradient} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        text-align: center !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        white-space: pre-line !important;
        height: auto !important;
        min-height: 90px !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
        transition: left 0.5s !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button:hover::before {{
        left: 100% !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button:active {{
        transform: translateY(-1px) scale(1.01) !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15) !important;
    }}
    /* Style the text inside the button */
    div[data-testid="stButton"][data-testid="{key}"] > button > div {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button > div > div:first-child {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.25rem !important;
        line-height: 1.2 !important;
    }}
    div[data-testid="stButton"][data-testid="{key}"] > button > div > div:last-child {{
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        opacity: 0.9 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def render_dashboard_metrics(metrics: Dict[str, Any]) -> None:
    """Render a row of clickable dashboard metrics."""
    cols = st.columns(len(metrics))

    gradients = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    ]

    for i, (col, (key, metric)) in enumerate(zip(cols, metrics.items())):
        with col:
            gradient = gradients[i % len(gradients)]
            button_key = f"card_{key}"
            button_text = f"{metric.get('value', 'N/A')}\n{metric.get('title', key)}"
            inject_button_style(button_key, gradient)
            if st.button(
                button_text,
                key=button_key,
                help=f"Click to edit {metric.get('title', key).lower()}",
                use_container_width=True
            ):
                # Open appropriate dialog based on metric type
                if key == "depth":
                    edit_depth_dialog()
                elif key == "wavelength":
                    edit_wavelength_dialog()
                elif key == "water":
                    edit_water_dialog()
                elif key == "anisotropy":
                    edit_anisotropy_dialog()
                elif key == "fluorophores":
                    edit_fluorophores_dialog()
                elif key == "laser":
                    edit_laser_dialog()
                elif key == "scattering_power":
                    edit_scattering_power_dialog()
                elif key == "scattering_scale":
                    edit_scattering_scale_dialog()


def create_collapsible_section(title: str, content_func, default_expanded: bool = False, help_text: str = None) -> None:
    """Create a collapsible section using a checkbox toggle."""
    help_text = help_text or f"Toggle {title.lower()} section"

    # Create a unique key for the checkbox
    key = f"show_{title.lower().replace(' ', '_').replace('🧮', '').replace('📊', '').strip()}"

    show_section = st.checkbox(
        f"Show {title}",
        value=default_expanded,
        help=help_text,
        key=key
    )

    if show_section:
        with st.container():
            content_func()
    else:
        st.info(f"👆 Check the box above to view {title.lower()}")


def add_dashboard_css() -> None:
    """Add custom CSS for dashboard styling."""
    st.markdown("""
    <style>
    /* Compact main container */
    .main > div {
        padding-top: 0.5rem;
    }
    
    /* Compact tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
        background-color: #f8f9fa;
        padding: 0.25rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding-left: 15px;
        padding-right: 15px;
        background-color: transparent;
        border-radius: 6px;
        border: none;
        color: #666;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0f4c81;
        color: white;
    }
    
    /* Compact expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        padding: 0.5rem 1rem;
    }
    
    /* Compact metric styling */
    .metric-card {
        background: white;
        padding: 0.75rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #0f4c81;
        margin: 0.25rem 0;
    }
    
    /* Compact button styling */
    .stButton > button {
        border-radius: 15px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    
    /* Base styling for metric cards - individual gradients applied inline */
    
    /* Reduce spacing between elements */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Compact section headers */
    h4 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Dialog styling - make dialogs much wider */
    .stDialog > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        width: 95vw !important;
        max-width: 1600px !important;
    }
    
    /* Specifically for fluorophore dialog - make it extremely wide */
    .stDialog:has([data-testid*="dialog"]) > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        width: 98vw !important;
        max-width: 1800px !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
