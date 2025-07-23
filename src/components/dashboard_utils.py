"""Dashboard utilities for consistent styling and layout."""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional


def create_metric_card(title: str, value: str, gradient: str, subtitle: Optional[str] = None) -> str:
    """Create a styled metric card with gradient background."""
    subtitle_html = f"<p style='margin: 0.25rem 0 0 0; opacity: 0.8; font-size: 0.75rem;'>{subtitle}</p>" if subtitle else ""
    
    return f"""
    <div style='background: {gradient}; 
                padding: 1rem; 
                border-radius: 8px; 
                text-align: center; 
                color: white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin-bottom: 0.5rem;
                cursor: pointer;
                transition: transform 0.2s ease;'>
        <h4 style='margin: 0; font-size: 1.5rem; font-weight: 600;'>{value}</h4>
        <p style='margin: 0.25rem 0 0 0; opacity: 0.9; font-size: 0.85rem;'>{title}</p>
        {subtitle_html}
    </div>
    """


@st.dialog("Edit Depth")
def edit_depth_dialog():
    """Dialog for editing tissue depth."""
    from src.config import DEFAULT_TISSUE_PARAMS
    
    current_depth = st.session_state.tissue_params.get("depth", DEFAULT_TISSUE_PARAMS["depth"])
    
    st.write("Adjust the tissue penetration depth:")
    
    new_depth = st.slider(
        "Depth (mm)",
        min_value=0.1,
        max_value=5.0,
        value=current_depth,
        step=0.1,
        help="Tissue penetration depth for analysis"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply", type="primary", use_container_width=True):
            st.session_state.tissue_params["depth"] = new_depth
            st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


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
            st.warning("⚠️ Normalization wavelength should be within the analysis range")
    
    st.divider()
    
    # Apply/Cancel buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Changes", type="primary", use_container_width=True):
            st.session_state.global_params["normalization_wavelength"] = new_wavelength
            st.session_state.global_params["wavelength_range"] = new_range
            st.success("Wavelength settings updated!")
            st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Edit Water Content")
def edit_water_dialog():
    """Dialog for editing tissue water content."""
    from src.config import DEFAULT_TISSUE_PARAMS
    
    current_water = st.session_state.tissue_params.get("water_content", DEFAULT_TISSUE_PARAMS["water_content"])
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply", type="primary", use_container_width=True):
            st.session_state.tissue_params["water_content"] = new_water_percent / 100
            st.rerun()
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Laser Configuration", width="large")
def edit_laser_dialog():
    """Dialog for laser configuration."""
    st.write("Configure laser settings:")
    
    try:
        from src.components.laser_manager import render_laser_manager
        render_laser_manager()
    except Exception as e:
        st.error(f"Error loading laser configuration: {e}")
    
    # Close button
    st.divider()
    if st.button("Close", use_container_width=True):
        st.rerun()


@st.dialog("Manage Fluorophores", width="large")
def edit_fluorophores_dialog():
    """Dialog for managing fluorophores with cross-section data."""
    st.write("View cross-section data and manage your fluorophore selection:")
    
    # Create tabs for different views - Manage Selection first
    tab1, tab2, tab3 = st.tabs(["✏️ Manage Selection", "📊 Cross-Section Data", "🔍 FPbase Search"])
    
    with tab1:
        # Show the existing fluorophore data editor
        try:
            from src.components.common import render_fluorophore_data_editor
            render_fluorophore_data_editor()
        except Exception as e:
            st.error(f"Error loading fluorophore editor: {e}")
    
    with tab2:
        # Show the fluorophore viewer with cross-section data
        try:
            from src.utils.data_loader import load_cross_section_data
            from src.components.fluorophore_viewer import render_fluorophore_viewer
            
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
                        existing_names = st.session_state.fluorophore_df.get('name', pd.Series()).tolist()
                        if selected_fluorophore in existing_names:
                            st.warning(f"{selected_fluorophore} is already in your selection.")
                        else:
                            # Add new fluorophore (simplified - you may need to adjust based on your data structure)
                            new_row = pd.DataFrame({
                                'name': [selected_fluorophore],
                                'visible': [True]
                            })
                            st.session_state.fluorophore_df = pd.concat([st.session_state.fluorophore_df, new_row], ignore_index=True)
                            st.success(f"Added {selected_fluorophore} to analysis!")
                            st.rerun()
                    else:
                        # First fluorophore
                        st.session_state.fluorophore_df = pd.DataFrame({
                            'name': [selected_fluorophore],
                            'visible': [True]
                        })
                        st.success(f"Added {selected_fluorophore} to analysis!")
                        st.rerun()
            else:
                st.error("Could not load cross-section data.")
        except Exception as e:
            st.error(f"Error loading fluorophore data: {e}")
    
    with tab3:
        # Show the FPbase search functionality
        try:
            from src.api.search_form import render_search_panel
            render_search_panel(key_prefix="dialog_search_")
        except Exception as e:
            st.error(f"Error loading FPbase search: {e}")
    
    # Close button
    st.divider()
    if st.button("Close", use_container_width=True):
        st.rerun()


def create_info_card(title: str, content: str, icon: str = "ℹ️") -> str:
    """Create an information card with consistent styling."""
    return f"""
    <div style='background: white; 
                border: 1px solid #e0e0e0;
                border-left: 4px solid #0f4c81;
                padding: 1rem; 
                border-radius: 5px; 
                margin: 1rem 0;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);'>
        <h4 style='margin: 0 0 0.5rem 0; color: #0f4c81;'>{icon} {title}</h4>
        <p style='margin: 0; color: #666;'>{content}</p>
    </div>
    """


def create_section_header(title: str, subtitle: Optional[str] = None) -> None:
    """Create a consistent section header."""
    subtitle_html = f"<p style='color: #666; font-size: 1.1rem; margin: 0.5rem 0 1rem 0;'>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
    <div style='margin: 2rem 0 1rem 0;'>
        <h2 style='color: #0f4c81; margin: 0; font-size: 1.8rem; border-bottom: 2px solid #0f4c81; padding-bottom: 0.5rem;'>
            {title}
        </h2>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def create_status_badge(status: str, color: str = "green") -> str:
    """Create a status badge."""
    color_map = {
        "green": "#28a745",
        "blue": "#007bff", 
        "orange": "#fd7e14",
        "red": "#dc3545",
        "gray": "#6c757d"
    }
    
    bg_color = color_map.get(color, color_map["gray"])
    
    return f"""
    <span style='background: {bg_color}; 
                 color: white; 
                 padding: 0.25rem 0.75rem; 
                 border-radius: 15px; 
                 font-size: 0.8rem; 
                 font-weight: 500;'>
        {status}
    </span>
    """


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
            
            # Create clickable card using button with custom styling
            button_text = f"{metric.get('value', 'N/A')}\n{metric.get('title', key)}"
            if st.button(
                button_text,
                key=f"card_{key}",
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
                elif key == "fluorophores":
                    edit_fluorophores_dialog()
                elif key == "laser":
                    edit_laser_dialog()
            
            # Apply custom styling to make the button look like the original card
            st.markdown(f"""
            <style>
            .stButton[data-testid="card_{key}"] > button {{
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
            
            .stButton[data-testid="card_{key}"] > button::before {{
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: -100% !important;
                width: 100% !important;
                height: 100% !important;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
                transition: left 0.5s !important;
            }}
            
            .stButton[data-testid="card_{key}"] > button:hover {{
                transform: translateY(-3px) scale(1.02) !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2) !important;
            }}
            
            .stButton[data-testid="card_{key}"] > button:hover::before {{
                left: 100% !important;
            }}
            
            .stButton[data-testid="card_{key}"] > button:active {{
                transform: translateY(-1px) scale(1.01) !important;
                box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15) !important;
            }}
            
            /* Style the text inside the button */
            .stButton[data-testid="card_{key}"] > button > div {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                height: 100% !important;
            }}
            
            .stButton[data-testid="card_{key}"] > button > div > div:first-child {{
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                margin-bottom: 0.25rem !important;
                line-height: 1.2 !important;
            }}
            
            .stButton[data-testid="card_{key}"] > button > div > div:last-child {{
                font-size: 0.85rem !important;
                font-weight: 500 !important;
                opacity: 0.9 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.5px !important;
            }}
            </style>
            """, unsafe_allow_html=True)


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