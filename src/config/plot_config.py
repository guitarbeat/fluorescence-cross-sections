from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Add shared configuration at module level
SHARED_PLOT_CONFIG = {
    "height": 600,
    "width": 600,  # Make plots square
    "margin": dict(t=50, r=50, b=50, l=50),
    "font": dict(
        family="Arial, sans-serif",
        size=14,
    ),
    "showgrid": False,  # Remove grid lines
    "zeroline": False,
}


@dataclass
class CrossSectionPlotConfig:
    # Plot dimensions and margins
    height: int = SHARED_PLOT_CONFIG["height"]
    width: int = SHARED_PLOT_CONFIG["width"]
    margin: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["margin"])
    font: dict = field(default_factory=lambda: SHARED_PLOT_CONFIG["font"])

    # Axis configurations
    wavelength_range: Tuple[float, float] = (700, 1600)
    cross_section_range: Tuple[int, int] = (1, 3)  # log scale from 10 to 1000 GM

    # Background heatmap settings
    heatmap_colorscale: List[List] = field(
        default_factory=lambda: [
            [0, "rgb(255, 200, 200)"],  # Light red for minimum
            [0.4, "rgb(255, 220, 220)"],  # Slightly lighter red
            [0.5, "rgb(255, 255, 255)"],  # White at threshold
            [1, "rgb(200, 200, 255)"],  # Light blue for maximum
        ]
    )
    heatmap_opacity: float = 0.7

    # Marker settings
    marker_size: int = 10
    default_marker_styles: Dict[str, Tuple[str, str]] = field(
        default_factory=lambda: {
            "Dana et al. (2016)": ("circle", "#1f77b4"),
            "Drobizhev et al. (2011)": ("square", "#000000"),
            "Janelia, Harris Lab": ("diamond", "#e377c2"),
            "Kobat et al. (2009)": ("triangle-up", "#17becf"),
            "Xu et al. (1996)": ("triangle-down", "#7f7f7f")
        }
    )

    # Layout settings
    title: str = "Two-Photon Cross Sections"
    legend_bgcolor: str = "rgba(255, 255, 255, 0.8)"

    def get_layout(self) -> dict:
        """Return the plotly layout configuration"""
        return {
            "title": dict(
                text=self.title, font=dict(size=16)  # Slightly larger title font
            ),
            "xaxis": dict(
                title="Wavelength (nm)",
                range=self.wavelength_range,
                showgrid=SHARED_PLOT_CONFIG["showgrid"],
                zeroline=SHARED_PLOT_CONFIG["zeroline"],
                titlefont=self.font,
                tickfont=self.font,
            ),
            "yaxis": dict(
                title="2PA Cross Section (GM)",
                type="log",
                range=self.cross_section_range,
                showgrid=SHARED_PLOT_CONFIG["showgrid"],
                zeroline=SHARED_PLOT_CONFIG["zeroline"],
                titlefont=self.font,
                tickfont=self.font,
            ),
            "margin": self.margin,
            "height": self.height,
            "width": self.width,
            "showlegend": True,
            "legend": dict(
                bgcolor=self.legend_bgcolor, title="Reference", font=self.font
            ),
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
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
            "paper_bgcolor": "white",
            "plot_bgcolor": "white",
            "showlegend": False,
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
