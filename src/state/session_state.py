"""Initialize and manage Streamlit session state."""
import logging
from pathlib import Path
from typing import List, Dict

import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI
from src.components.laser_manager import initialize_laser_data
from src.config.plot_config import SHARED_PLOT_CONFIG
from src.config.tissue_config import DEFAULT_TISSUE_PARAMS
from src.utils.data_loader import (
    load_fluorophore_data,
    load_cross_section_data,
    load_water_absorption_data
)

logger = logging.getLogger(__name__)

# Default parameters - derived from plot_config
DEFAULT_GLOBAL_PARAMS = {
    "wavelength_range": (
        SHARED_PLOT_CONFIG.get("wavelength_range", (700, 1700))
    ),  # Use plot config or fallback
    "normalization_wavelength": 1300,
    "absorption_threshold": 50,
}

# Use DEFAULT_TISSUE_PARAMS from tissue_config instead of redefining
DEFAULT_COLUMNS: List[str] = [
    "Name",
    "Wavelength",
    "Cross_Section",
    "Reference",
    "Ex_Max",
    "Em_Max",
    "QY",
    "EC",
    "pKa",
    "Brightness",
]


def compile_fluorophore_data(cross_sections: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Compile peak wavelengths and other statistics into a single DataFrame.
    """
    data = []
    for name, df in cross_sections.items():
        stats = {}
        stats['Name'] = name
        
        if name == "IntrinsicFluorophores":
            # Handle multiple fluorophores
            for col in ["riboflavin", "folic_acid", "cholecalciferol", "retinol"]:
                peak_idx = df[col].idxmax()
                stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
                stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
        
        elif name == "NADH-ProteinBound":
            # Handle protein-bound forms
            for col in ["gm_mean", "gm_mdh", "gm_ad"]:
                peak_idx = df[col].idxmax()
                stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
                stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
        
        else:
            # Standard single-peak fluorophores
            cross_section_col = "cross_section" if "cross_section" in df.columns else df.columns[1]
            peak_idx = df[cross_section_col].idxmax()
            stats["peak_wavelength"] = df.loc[peak_idx, "wavelength"]
            stats["peak_cross_section"] = df.loc[peak_idx, cross_section_col]
            
        data.append(stats)
    
    return pd.DataFrame(data)


def initialize_session_state() -> None:
    """Initialize or reset session state variables."""
    session_state = st.session_state

    # Initialize API client
    session_state.setdefault("fpbase_client", FPbaseAPI())

    # Load cross-section data
    cross_sections = load_cross_section_data()
    session_state.setdefault("cross_sections", cross_sections)

    # Compile peak data
    peak_data = compile_fluorophore_data(cross_sections)
    session_state.setdefault("peak_data", peak_data)

    # Initialize other dataframes
    session_state.setdefault("fluorophore_df", load_fluorophore_data())
    session_state.setdefault("search_results", pd.DataFrame(columns=DEFAULT_COLUMNS))

    # Initialize global parameters with plot config values
    global_params = DEFAULT_GLOBAL_PARAMS.copy()
    if "wavelength_range" in SHARED_PLOT_CONFIG:
        global_params["wavelength_range"] = SHARED_PLOT_CONFIG["wavelength_range"]
    session_state.setdefault("global_params", global_params)

    # Initialize tissue parameters from tissue_config
    session_state.setdefault("tissue_params", DEFAULT_TISSUE_PARAMS.copy())

    # Initialize laser data
    session_state.setdefault("laser_df", initialize_laser_data())
    session_state.setdefault("show_lasers",True)

    # Initialize plot configuration
    session_state.setdefault("plot_config", SHARED_PLOT_CONFIG.copy())
