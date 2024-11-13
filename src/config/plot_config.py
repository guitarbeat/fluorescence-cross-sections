from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import streamlit as st
from streamlit_theme import st_theme

# Add shared configuration at module level
SHARED_PLOT_CONFIG = {
    "autosize": True,  # Let Plotly handle sizing
    "height": 800,     # Default height
    "width": 800,      # Default width
    "margin": dict(t=50, r=50, b=50, l=50),
    "font": dict(
        family="Arial, sans-serif",
        size=14,
    ),
    "showgrid": False,
    "zeroline": False,
}

# Default theme colors
LIGHT_THEME = {
    "bgcolor": "rgba(255, 255, 255, 0.9)",     # Light background
    "bordercolor": "rgba(128, 128, 128, 0.2)",  # Subtle border for light theme
    "font_color": "#2E2E2E"                     # Dark text for light theme
}

DARK_THEME = {
    "bgcolor": "rgba(32, 32, 32, 0.9)",     # Dark background
    "bordercolor": "rgba(128, 128, 128, 0.3)",  # Subtle border for dark theme
    "font_color": "#FFFFFF"                     # White text for dark theme
}

def get_theme_colors():
    """Get theme-aware colors based on Streamlit theme"""
    if st.session_state.get("theme") == "dark":
        return DARK_THEME
    return LIGHT_THEME

# Initialize with light theme by default
FLOATING_ELEMENT_THEME = {
    "font": dict(
        family="Arial, sans-serif",
        size=10,
        color=LIGHT_THEME["font_color"]  # Default to light theme
    ),
    "bgcolor": LIGHT_THEME["bgcolor"],
    "bordercolor": LIGHT_THEME["bordercolor"],
    "borderwidth": 1,
}

def update_floating_element_theme():
    """Update theme colors based on current theme"""
    theme = get_theme_colors()
    FLOATING_ELEMENT_THEME.update({
        "font": dict(
            family="Arial, sans-serif",
            size=10,
            color=theme["font_color"]
        ),
        "bgcolor": theme["bgcolor"],
        "bordercolor": theme["bordercolor"],
    })

@dataclass
class CrossSectionPlotConfig:
    # Plot dimensions and margins
    height: int = SHARED_PLOT_CONFIG["height"]
    width: int = SHARED_PLOT_CONFIG["width"]
    margin: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["margin"])
    font: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["font"])

    # Axis configurations
    wavelength_range: Tuple[float, float] = (700, 1600)
    cross_section_range: Tuple[int, int] = (0.5, 2.5)  # log10 scale: ~3 GM to ~300 GM
    heatmap_extension_factor: float = 3.0  # Extend heatmap further beyond visible range

    # Background heatmap settings
    heatmap_colorscale: List[List] = field(
        default_factory=lambda: [
            [0, "rgba(255, 180, 180, 0.5)"],     # Stronger light red
            [0.4, "rgba(255, 220, 220, 0.4)"],   # Medium light red
            [0.5, "rgba(220, 220, 255, 0.4)"],   # Medium light blue
            [1, "rgba(180, 180, 255, 0.5)"],     # Stronger light blue
        ]
    )
    heatmap_opacity: float = 0.6  # Slightly reduced opacity

    # Marker settings
    marker_size: int = 12
    default_marker_styles: Dict[str, Tuple[str, str]] = field(
        default_factory=lambda: {
            "Dana et al. (2016)": ("circle", "#1f77b4"),         # Classic blue
            "Drobizhev et al. (2011)": ("square", "#2c2c2c"),    # Dark gray
            "Janelia, Harris Lab": ("diamond", "#e377c2"),       # Pink
            "Kobat et al. (2009)": ("triangle-up", "#17becf"),   # Turquoise
            "Xu et al. (1996)": ("triangle-down", "#7f7f7f")     # Medium gray
        }
    )

    # Layout settings
    title: str = "Two-Photon Cross Sections"
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)"  # Light background with transparency

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
                text=self.title,
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
                constrain="domain",  # Constrain axis to maintain aspect ratio
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
                scaleanchor="x",  # Lock aspect ratio
                scaleratio=1,     # 1:1 ratio
                constrain="domain",  # Constrain axis to maintain aspect ratio
            ),
            "margin": self.margin,
            "autosize": True,
            "showlegend": True,
            "legend": dict(
                title=dict(
                    text="",
                    font=FLOATING_ELEMENT_THEME["font"]
                ),
                font=FLOATING_ELEMENT_THEME["font"],
                bgcolor=FLOATING_ELEMENT_THEME["bgcolor"],
                bordercolor=FLOATING_ELEMENT_THEME["bordercolor"],
                borderwidth=FLOATING_ELEMENT_THEME["borderwidth"],
                xanchor="right",
                x=0.98,
                y=0.82,
                yanchor="top",
                orientation="v",
                itemwidth=30,
                itemsizing="constant",
                entrywidth=150,
                entrywidthmode="pixels",
                tracegroupgap=5,
            ),
            "coloraxis": dict(
                colorbar=dict(
                    title="Normalized<br>Photon<br>Fraction",
                    titlefont=FLOATING_ELEMENT_THEME["font"],
                    tickfont=FLOATING_ELEMENT_THEME["font"],
                    len=0.3,
                    x=0.98,
                    y=0.15,
                    xanchor="right",
                    yanchor="bottom",
                    bgcolor=FLOATING_ELEMENT_THEME["bgcolor"],
                    bordercolor=FLOATING_ELEMENT_THEME["bordercolor"],
                    borderwidth=FLOATING_ELEMENT_THEME["borderwidth"],
                    outlinewidth=0,
                )
            ),
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "width": self.width,   # Set fixed width
            "height": self.width,  # Set height equal to width
        }


@dataclass
class TissuePlotConfig:
    # Plot dimensions and styling
    height: int = SHARED_PLOT_CONFIG["height"]
    width: int = SHARED_PLOT_CONFIG["width"]
    margin: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["margin"])
    font: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["font"])
    
    # Add wavelength range like CrossSectionPlotConfig
    wavelength_range: Tuple[float, float] = (700, 2400)

    # Line styling
    photon_fraction_line: dict = field(
        default_factory=lambda: dict(color="blue", width=2)
    )
    absorption_line: dict = field(
        default_factory=lambda: dict(
            color="red",
            width=2,
            solid="solid",
            dotted="dot"
        )
    )

    # Shading configuration
    absorption_shape: dict = field(
        default_factory=lambda: dict(
            fillcolor="rgba(255, 0, 0, 0.1)",
            line_width=0,
            layer="below"
        )
    )

    # Axis configurations
    y_axis_range: Tuple[float, float] = (0, 2)  # For photon fraction
    y2_axis_range: Tuple[float, float] = (0, 100)  # For absorption percentage

    def get_layout(self) -> dict:
        """Return the plotly layout configuration"""
        return {
            "height": self.height,
            "width": self.width,
            "margin": self.margin,
            "showlegend": False,
            "font": self.font,
        }

    def get_photon_trace(self, wavelengths: list, normalized_fraction: list) -> dict:
        """Return configuration for photon fraction trace"""
        return dict(
            x=wavelengths,
            y=normalized_fraction,
            name="Normalized Photon Fraction",
            line=self.photon_fraction_line,
            showlegend=False,
        )

    def get_absorption_trace(
        self, wavelengths: list, absorption: list, is_above_threshold: bool
    ) -> dict:
        """Return configuration for absorption trace"""
        return dict(
            x=wavelengths,
            y=absorption,
            mode="lines",
            line=dict(
                color=self.absorption_line["color"],
                width=self.absorption_line["width"],
                dash=self.absorption_line["solid"] if is_above_threshold else self.absorption_line["dotted"],
            ),
            showlegend=False,
            name="Water Absorption",
        )
