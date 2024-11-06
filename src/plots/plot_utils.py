"""Shared utilities for plot creation and styling."""
from typing import Optional, List
import plotly.graph_objects as go
from ..models.plot_config import get_theme_colors
import streamlit as st

def add_lasers_to_plot(fig, y_position: float = 1.0, domain: Optional[List[float]] = None) -> None:
    """Add laser annotations to plot in a separate domain above the main plot."""
    if not st.session_state.get("show_lasers", True):
        return

    # Default domain places lasers above main plot
    if domain is None:
        domain = [0, 0.08]  # 8% of plot height for lasers

    # Create a new y-axis for lasers
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            yaxis="y2",
            showlegend=False,
        )
    )

    # Configure the laser axis
    fig.update_layout(
        yaxis2=dict(
            domain=domain,
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[0, 1],  # Fixed range for laser annotations
            fixedrange=True,  # Prevent zooming/panning
        )
    )

    # Add laser annotations
    if hasattr(st.session_state, 'laser_df'):
        for _, laser in st.session_state.laser_df.iterrows():
            # Add shaded region for laser range
            fig.add_shape(
                type="rect",
                x0=laser["Start_nm"],
                x1=laser["End_nm"],
                y0=0,
                y1=1,
                fillcolor=laser["Color"],
                opacity=0.3,
                layer="above",
                line_width=0,
                yref="y2",
            )
            
            # Add laser label
            fig.add_annotation(
                x=(laser["Start_nm"] + laser["End_nm"]) / 2,
                y=0.5,
                text=laser["Name"],
                showarrow=False,
                yref="y2",
                font=dict(size=10, color=laser["Color"]),
            )

def apply_common_styling(
    fig: go.Figure,
    title: str,
    xaxis_title: str = "Wavelength (nm)",
    yaxis_title: str = "",
    xaxis_range: tuple = (800, 2400)
) -> None:
    """Apply consistent styling across plots."""
    theme = get_theme_colors()
    
    fig.update_layout(
        template=theme["plot_template"],
        title=dict(
            text=title,
            font=dict(color=theme["text_color"])
        ),
        xaxis=dict(
            title=xaxis_title,
            range=xaxis_range,
            showgrid=True,
            gridwidth=1,
            gridcolor=theme["grid_color"],
            zeroline=False,
            tickfont=dict(color=theme["text_color"]),
            title_font=dict(color=theme["text_color"])
        ),
        plot_bgcolor=theme["bg_color"],
        paper_bgcolor=theme["bg_color"],
        margin=dict(t=50, r=50, b=50, l=50),
        height=600,
    ) 