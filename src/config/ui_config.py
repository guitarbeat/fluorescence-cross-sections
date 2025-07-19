"""
UI configuration constants for consistent styling and behavior.

This module centralizes UI-related constants to ensure consistency
across the application and make maintenance easier.
"""

# Plot configuration
PLOT_CONFIG = {
    "default_height": 400,
    "small_height": 250,
    "large_height": 600,
    "margin": dict(l=20, r=20, t=40, b=20),
    "small_margin": dict(l=20, r=20, t=40, b=20),
    "hovermode": 'x unified',
    "showlegend": False,
    "aspect_ratio": 1.2,
}

# Data editor configuration
DATA_EDITOR_CONFIG = {
    "num_rows": "dynamic",
    "use_container_width": True,
    "hide_index": True,
}

# Column configurations for data editors
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

# Default column order
FLUOROPHORE_COLUMN_ORDER = ["Visible", "Name", "Wavelength", "Cross_Section", "Reference"]

# Parameter control configurations
PARAMETER_CONFIGS = {
    "wavelength_range": {
        "min_value": 700,
        "max_value": 2400,
        "step": 10,
    },
    "normalization_wavelength": {
        "min_value": 800,
        "max_value": 2400,
        "step": 10,
    },
    "tissue_depth": {
        "min_value": 0.1,
        "max_value": 2.0,
        "step": 0.01,
    },
    "water_content": {
        "options": [i / 100 for i in range(0, 105, 5)],
    },
    "anisotropy": {
        "min_value": 0.0,
        "max_value": 1.0,
        "step": 0.05,
    },
    "scattering_power": {
        "min_value": 0.5,
        "max_value": 2.0,
        "step": 0.05,
    },
    "scattering_scale": {
        "min_value": 0.5,
        "max_value": 2.0,
        "step": 0.1,
    },
}

# UI text constants
UI_TEXTS = {
    "titles": {
        "main": "Deep Tissue Imaging Optimizer",
        "wavelength_settings": "Wavelength Settings",
        "tissue_parameters": "Tissue Parameters",
        "laser_configuration": "Laser Configuration",
        "cross_sections_analysis": "Cross-sections Analysis",
        "tissue_penetration_analysis": "Tissue Penetration Analysis",
        "tissue_penetration_model": "Tissue Penetration Mathematical Model",
        "fluorophore_discovery": "Fluorophore Discovery",
        "fluorophore_data": "Fluorophore Data",
    },
    "descriptions": {
        "tissue_penetration_model": "Detailed mathematical analysis of tissue penetration with interactive controls",
        "fluorophore_discovery": "Browse, search, and manage your fluorophore database",
    },
    "labels": {
        "analysis_range": "Analysis Range (nm)",
        "normalization_wavelength": "Normalization λ (nm)",
        "tissue_depth": "Tissue Depth (mm)",
        "water_content": "Water Content",
        "anisotropy": "Anisotropy (g)",
        "scattering_power": "Scattering Power (b)",
        "scattering_scale": "Scattering Scale (a)",
        "show_all_fluorophores": "Show All Fluorophores",
        "save_changes": "Save Changes",
        "reset_parameters": "↺ Reset Parameters",
    },
    "help_texts": {
        "analysis_range": "Wavelength range for analysis",
        "normalization_wavelength": "Wavelength for normalization",
        "tissue_depth": "Depth of tissue penetration",
        "water_content": "Fraction of tissue that is water (≈75% for brain)",
        "anisotropy": "Controls directional scattering: g=0 (isotropic) to g=1 (forward only)",
        "scattering_power": "Wavelength dependence (≈1.37 for brain tissue)",
        "scattering_scale": "Scattering amplitude [mm⁻¹]",
        "show_all_fluorophores": "Toggle visibility of all fluorophores",
    },
    "messages": {
        "no_data": "No data to display - try searching for fluorophores.",
        "no_fluorophore_data": "No data in fluorophore table yet. Add fluorophores from the Fluorophore Library tab.",
        "changes_saved": "Changes saved!",
        "save_failed": "Failed to save changes: {error}",
    },
    "info_messages": {
        "cross_section_data": "Browse the complete library of two-photon cross section data.\nSelect a fluorophore to view its detailed data and add it to your main table.",
        "fpbase_search": "Search the FPbase database for additional fluorophores.\nFound proteins can be added to your main fluorophore table.",
    },
}

# Tab configurations
TAB_CONFIGS = {
    "fluorophore_discovery": [
        ("Cross Section Data", None, UI_TEXTS["info_messages"]["cross_section_data"]),
        ("FPbase Search", None, UI_TEXTS["info_messages"]["fpbase_search"]),
    ],
}

# Error messages
ERROR_MESSAGES = {
    "laser_configuration": "Error loading laser configuration",
    "cross_sections": "Error loading cross-sections",
    "tissue_penetration": "Error loading tissue penetration",
    "mathematical_analysis": "Error loading mathematical tissue analysis",
    "fluorophore_library": "Error loading fluorophore library",
    "footer": "Error loading footer",
}

# Fallback messages
FALLBACK_MESSAGES = {
    "tissue_penetration": "Please check the tissue penetration component implementation.",
    "mathematical_analysis": "Please check the tissue configuration component implementation.",
}
