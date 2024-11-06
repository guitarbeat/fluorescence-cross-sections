"""Configuration for tissue penetration modeling."""

from typing import Dict, Tuple, Any

# Laser configurations
LASER_RANGES: Dict[str, Tuple[int, int]] = {
    "Ti:Sapphire": (800, 1000),
    "Yb fiber": (1050, 1070),
    "2C2P": (1150, 1200),
    "Diamond": (1250, 1300),
    "Er fiber": (1550, 1600),
    "OPO/OPA": (1100, 2200),
}

# Default tissue parameters to match the paper
DEFAULT_TISSUE_PARAMS = {
    "depth": 1.0,  # 1mm depth as shown in image
    "water_content": 0.75,  # 75% as specified
    "g": 0.9,  # Matches paper
    "a": 1.1,  # 1.1 mm^-1 as specified
    "b": 1.37,  # Matches paper
    "absorption_threshold": 50,  # Percentage threshold for shading
    "normalization_wavelength": 1300,  # Wavelength to normalize at
    "two_photon": {
        "enabled": False,  # Switch for two-photon comparison
        "lambda_a": 800,  # First wavelength
        "lambda_b": 1040,  # Second wavelength
    }
}

# Wavelength ranges for different phenomena
WAVELENGTH_RANGES = {
    "water_peaks": [1450, 1950],  # Major water absorption peaks
    "optimal_windows": [1300, 1700],  # Optimal imaging windows
    "absorption_threshold": 50,  # Percentage threshold for high absorption
}

# Formula configurations
TISSUE_FORMULA_CONFIG = {
    "title": "Light Penetration in Tissue",
    "main_formula": (r"T(\lambda, z) = e^{-(\mu_s(\lambda) + \mu_a(\lambda))z}"),
    "explanation": (
        "The transmission of light through tissue depends on both scattering and absorption:\n\n"
        "1. **Scattering ($\\mu_s$):** Decreases with increasing wavelength\n"
        "2. **Absorption ($\\mu_a$):** Increases significantly near 1500 nm and beyond 1800 nm\n"
        "3. **Depth ($z$):** Distance light travels through tissue\n\n"
        "Scattered excitation light does not contribute to multiphoton absorption, "
        "making the wavelength choice crucial for deep tissue imaging."
    ),
    "additional_formulas": [
        {
            "title": "Scattering Coefficient",
            "formula": (
                r"\mu_s(\lambda) = \frac{a}{1-g} \cdot "
                r"\left(\frac{\lambda}{500}\right)^{-b}"
            ),
            "explanation": (
                "**Wavelength Dependence of Scattering:**\n\n"
                "- $g$: Scattering anisotropy ≈ 0.9 for biological tissues\n"
                "  - Describes directional distribution of scattered light\n"
                "  - $g = 0$: Isotropic scattering\n"
                "  - $g = 1$: Pure forward scattering\n\n"
                "- $a$: Scattering amplitude [mm⁻¹]\n"
                "  - Varies even within brain tissue\n"
                "  - Typical value ≈ 1.1 mm⁻¹\n\n"
                "- $b$: Scattering power ≈ 1.37\n"
                "  - Determines wavelength dependence\n"
                "  - Higher values indicate stronger wavelength dependence"
            ),
        },
        {
            "title": "Water Absorption",
            "formula": (
                r"\mu_a(\lambda) = \mu_{a,base} \cdot w + "
                r"\sum_{i} A_i e^{-\frac{(\lambda - \lambda_i)^2}{2\sigma_i^2}}"
            ),
            "explanation": (
                "**Key Features of Water Absorption:**\n\n"
                "- Major absorption peaks:\n"
                "  - First peak: 1450 nm\n"
                "  - Second peak: 1950 nm\n\n"
                "- Water content ($w$) ≈ 75% for brain tissue\n"
                "- Regions with >50% absorption may be unsuitable for deep imaging\n"
                "  - Excessive absorption causes tissue heating\n"
                "  - Peak at 2200 nm is not feasible due to heating concerns"
            ),
        },
        {
            "title": "Optimal Imaging Windows",
            "formula": (
                r"\text{Optimal } \lambda \approx 1300 \text{ nm or } 1700 \text{ nm}"
            ),
            "explanation": (
                "**Advantages of Different Wavelengths:**\n\n"
                "1. **1300 nm window:**\n"
                "   - 15× more photons reach 1 mm depth vs. 800 nm\n"
                "   - Suitable for two- or three-photon excitation\n\n"
                "2. **1700 nm window:**\n"
                "   - 1.8× more photons vs. 1300 nm\n"
                "   - Primarily three-photon excitation\n"
                "   - Balances scattering and absorption\n\n"
                "3. **2200 nm peak:**\n"
                "   - Not viable due to >50% absorption\n"
                "   - Excessive tissue heating concerns"
            ),
        },
    ],
}

# Plot styling to match the reference image
PLOT_STYLE = {
    "colors": {
        "photon_fraction": "blue",  # Blue line for photon fraction
        "absorption": "red",  # Red line for absorption
        "absorption_fill": "rgba(255,0,0,0.2)",  # Light red shading for >50% absorption
    },
    "markers": {
        "laser": dict(symbol="star", size=15, color="green"),  # Green stars for lasers
    },
    "lines": {
        "laser_range": dict(
            color="green", 
            width=2, 
            dash="solid"
        ),  # Green arrows for laser ranges
    },
    "absorption_threshold": 50,  # 50% threshold for absorption shading
}
