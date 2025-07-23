"""Consolidated configuration for the Deep Tissue Imaging Optimizer."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st

# Project directories
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

# Common file paths
FLUOROPHORE_CSV = DATA_DIR / "fluorophores.csv"
LASER_CSV = DATA_DIR / "lasers.csv"

# Column definitions
FLUOROPHORE_COLUMNS = [
    "Name", "Wavelength", "Cross_Section", "Reference",
    "Em_Max", "Ex_Max", "QY", "EC", "pKa", "Brightness",
]

BASIC_FLUOROPHORE_COLUMNS = [
    "Name", "Wavelength", "Cross_Section", "Reference",
]

# Shared plot configuration
SHARED_PLOT_CONFIG = {
    "autosize": True,
    "height": 800,
    "width": 800,
    "margin": dict(t=50, r=50, b=50, l=50),
    "font": dict(family="Arial, sans-serif", size=14),
    "showgrid": False,
    "zeroline": False,
    "wavelength_range": (700, 1700),
}

# Theme colors
LIGHT_THEME = {
    "bgcolor": "rgba(255, 255, 255, 0.9)",
    "bordercolor": "rgba(128, 128, 128, 0.2)",
    "font_color": "#2E2E2E"
}

DARK_THEME = {
    "bgcolor": "rgba(32, 32, 32, 0.9)",
    "bordercolor": "rgba(128, 128, 128, 0.3)",
    "font_color": "#FFFFFF"
}

def get_theme_colors():
    """Get theme-aware colors based on Streamlit theme"""
    return DARK_THEME if st.session_state.get("theme") == "dark" else LIGHT_THEME

# Style configuration
STYLE_CONFIG = {
    "primary_color": "#0f4c81",
    "secondary_color": "#ff4b4b",
    "accent_color": "#17becf",
    "text_color": "#666666",
    "border_color": "rgba(128, 128, 128, 0.2)",
}

# Dashboard styling
DASHBOARD_STYLE = {
    "gradient_colors": {
        "blue": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "pink": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "cyan": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "green": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "purple": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "orange": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    },
    "card_style": {
        "padding": "1.5rem",
        "border_radius": "10px",
        "text_align": "center",
        "color": "white",
        "box_shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    },
    "section_spacing": "2rem",
}

# Floating element theme
FLOATING_ELEMENT_THEME = {
    "font": dict(
        family="Arial, sans-serif",
        size=12,
        color=STYLE_CONFIG["text_color"]
    ),
    "bgcolor": "rgba(255, 255, 255, 0.95)",
    "bordercolor": STYLE_CONFIG["border_color"],
    "borderwidth": 1,
}

def get_common_colorbar_config(title: str = "Normalized<br>Photon<br>Fraction",
                              x: float = 0.98,
                              y: float = 0.15,
                              len: float = 0.3,
                              tickvals: list = None,
                              ticktext: list = None) -> dict:
    """Get common colorbar configuration to eliminate duplicate code."""
    config = dict(
        title=title,
        tickfont=FLOATING_ELEMENT_THEME["font"],
        len=len,
        x=x,
        y=y,
        xanchor="right",
        yanchor="bottom",
        bgcolor=FLOATING_ELEMENT_THEME["bgcolor"],
        bordercolor=FLOATING_ELEMENT_THEME["bordercolor"],
        borderwidth=FLOATING_ELEMENT_THEME["borderwidth"],
        outlinewidth=0,
    )

    if tickvals is not None:
        config["tickvals"] = tickvals
    if ticktext is not None:
        config["ticktext"] = ticktext

    return config

# UI configuration
PLOT_CONFIG = {
    "default_height": 400,
    "small_height": 250,
    "large_height": 600,
    "margin": dict(l=20, r=20, t=40, b=20),
    "hovermode": 'x unified',
    "showlegend": False,
    "aspect_ratio": 1.2,
}

DATA_EDITOR_CONFIG = {
    "num_rows": "dynamic",
    "use_container_width": True,
    "hide_index": True,
}

FLUOROPHORE_COLUMN_CONFIG = {
    "Visible": {
        "type": "checkbox",
        "label": "Show",
        "help": "Toggle fluorophore visibility in plot",
        "default": True,
    },
    "Name": {
        "type": "text",
        "label": "Fluorophore",
        "help": "Fluorophore name",
    },
    "Wavelength": {
        "type": "number",
        "label": "2P λ (nm)",
        "help": "Two-photon excitation wavelength",
        "format": "%d",
    },
    "Cross_Section": {
        "type": "number",
        "label": "Cross Section (GM)",
        "help": "Two-photon cross section in Goeppert-Mayer units",
        "format": "%.2f",
    },
    "Reference": {
        "type": "text",
        "label": "Reference",
        "help": "Data source (Zipfel Lab or FPbase)",
    },
}

FLUOROPHORE_COLUMN_ORDER = ["Visible", "Name", "Wavelength", "Cross_Section", "Reference"]

# Parameter configurations
PARAMETER_CONFIGS = {
    "wavelength_range": {"min_value": 700, "max_value": 2400, "step": 10},
    "normalization_wavelength": {"min_value": 800, "max_value": 2400, "step": 10},
    "tissue_depth": {"min_value": 0.1, "max_value": 2.0, "step": 0.01},
    "water_content": {"options": [i / 100 for i in range(0, 105, 5)]},
    "anisotropy": {"min_value": 0.0, "max_value": 1.0, "step": 0.05},
    "scattering_power": {"min_value": 0.5, "max_value": 2.0, "step": 0.05},
    "scattering_scale": {"min_value": 0.5, "max_value": 2.0, "step": 0.1},
}

# UI text constants
UI_TEXTS = {
    "titles": {
        "main": "Deep Tissue Imaging Optimizer",
        "cross_sections_analysis": "Cross-sections Analysis",
        "tissue_penetration_analysis": "Tissue Penetration Analysis",
        "fluorophore_data": "Fluorophore Data",
    },
    "labels": {
        "show_all_fluorophores": "Show All Fluorophores",
        "save_changes": "Save Changes",
    },
    "help_texts": {
        "show_all_fluorophores": "Toggle visibility of all fluorophores",
    },
    "messages": {
        "no_fluorophore_data": "No data in fluorophore table yet. Add fluorophores from the Fluorophore Library tab.",
        "changes_saved": "Changes saved!",
    },
}

# Plot configuration classes
@dataclass
class CrossSectionPlotConfig:
    """Configuration for two-photon cross-section plots."""
    height: int = SHARED_PLOT_CONFIG["height"]
    width: int = SHARED_PLOT_CONFIG["width"]
    margin: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["margin"])
    font: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["font"])
    wavelength_range: Tuple[float, float] = (700, 1600)
    cross_section_range: Tuple[int, int] = (0.5, 2.5)
    heatmap_extension_factor: float = 3.0
    heatmap_opacity: float = 0.6
    marker_size: int = 12
    
    heatmap_colorscale: List[List] = field(
        default_factory=lambda: [
            [0, "rgba(255, 180, 180, 0.5)"],
            [0.4, "rgba(255, 220, 220, 0.4)"],
            [0.5, "rgba(220, 220, 255, 0.4)"],
            [1, "rgba(180, 180, 255, 0.5)"],
        ]
    )
    
    default_marker_styles: Dict[str, Tuple[str, str]] = field(
        default_factory=lambda: {
            "Dana et al. (2016)": ("circle", "#1f77b4"),
            "Drobizhev et al. (2011)": ("square", "#2c2c2c"),
            "Janelia, Harris Lab": ("diamond", "#e377c2"),
            "Kobat et al. (2009)": ("triangle-up", "#17becf"),
            "Xu et al. (1996)": ("triangle-down", "#7f7f7f")
        }
    )

    def get_extended_wavelength_range(self, current_range: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate extended wavelength range for heatmap"""
        range_width = current_range[1] - current_range[0]
        extension = range_width * (self.heatmap_extension_factor - 1) / 2
        return (
            current_range[0] - extension,
            current_range[1] + extension
        )

    def get_layout(self) -> dict:
        """Return the plotly layout configuration"""
        return {
            "title": dict(
                text="Two-Photon Cross Sections",
                font=dict(size=16)
            ),
            "xaxis": dict(
                title="Wavelength (nm)",
                range=self.wavelength_range,
                showgrid=True,
                gridcolor="rgba(128, 128, 128, 0.15)",
                zeroline=SHARED_PLOT_CONFIG["zeroline"],
                titlefont=self.font,
                tickfont=self.font,
                linecolor="rgba(128, 128, 128, 0.4)",
                constrain="domain",
            ),
            "yaxis": dict(
                title="Peak 2PA Cross Section (GM)",
                type="log",
                range=self.cross_section_range,
                showgrid=True,
                gridcolor="rgba(128, 128, 128, 0.15)",
                zeroline=SHARED_PLOT_CONFIG["zeroline"],
                titlefont=self.font,
                tickfont=self.font,
                linecolor="rgba(128, 128, 128, 0.4)",
                dtick=0.5,
                scaleanchor="x",
                scaleratio=1,
                constrain="domain",
            ),
            "margin": self.margin,
            "autosize": True,
            "showlegend": True,
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "width": self.width,
            "height": self.width,
        }

@dataclass
class TissuePlotConfig:
    """Configuration for tissue penetration plots."""
    height: int = SHARED_PLOT_CONFIG["height"]
    width: int = SHARED_PLOT_CONFIG["width"]
    margin: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["margin"])
    font: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["font"])
    wavelength_range: Tuple[float, float] = (700, 2400)
    
    photon_fraction_line: dict = field(
        default_factory=lambda: dict(color="blue", width=2)
    )
    absorption_line: dict = field(
        default_factory=lambda: dict(color="red", width=2)
    )

# Default parameters
DEFAULT_GLOBAL_PARAMS = {
    "wavelength_range": SHARED_PLOT_CONFIG["wavelength_range"],
    "normalization_wavelength": 1300,
    "absorption_threshold": 50,
}

DEFAULT_TISSUE_PARAMS = {
    "depth": 1.0,
    "water_content": 0.75,
    "g": 0.9,  # anisotropy parameter
    "b": 1.37,  # scattering_power
    "a": 1.0,   # scattering_scale
}