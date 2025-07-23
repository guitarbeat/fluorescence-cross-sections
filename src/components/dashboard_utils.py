"""Dashboard utilities for consistent styling and layout."""

import streamlit as st
from typing import Dict, Any, Optional


def create_metric_card(title: str, value: str, gradient: str, subtitle: Optional[str] = None) -> str:
    """Create a styled metric card with gradient background."""
    subtitle_html = f"<p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>{subtitle}</p>" if subtitle else ""
    
    return f"""
    <div style='background: {gradient}; 
                padding: 1.5rem; 
                border-radius: 10px; 
                text-align: center; 
                color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;'>
        <h3 style='margin: 0; font-size: 2rem; font-weight: 600;'>{value}</h3>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>{title}</p>
        {subtitle_html}
    </div>
    """


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
    """Render a row of dashboard metrics."""
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
            card_html = create_metric_card(
                title=metric.get("title", key),
                value=str(metric.get("value", "N/A")),
                gradient=gradient,
                subtitle=metric.get("subtitle")
            )
            st.markdown(card_html, unsafe_allow_html=True)


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
    /* Main container styling */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: transparent;
        border-radius: 8px;
        border: none;
        color: #666;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0f4c81;
        color: white;
    }
    
    /* Container styling */
    .stContainer > div {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #0f4c81;
        margin: 0.5rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 500;
    }
    
    /* Checkbox styling for collapsible sections */
    .stCheckbox > label {
        background-color: #f8f9fa;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        font-weight: 500;
        color: #0f4c81;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)