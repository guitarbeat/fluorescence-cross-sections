"""Initialize and manage Streamlit session state."""
import logging
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI
from src.components.laser_manager import initialize_laser_data
from src.config.plot_config import SHARED_PLOT_CONFIG
from src.config.tissue_config import DEFAULT_TISSUE_PARAMS

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


def load_fluorophore_data() -> pd.DataFrame:
    """Load existing fluorophores from CSV or create empty DataFrame."""
    try:
        fluorophore_df = pd.read_csv(Path("data/fluorophores.csv"))
        return fluorophore_df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        logger.warning(
            "No existing fluorophore data found, creating empty DataFrame")
        return pd.DataFrame(columns=DEFAULT_COLUMNS)


def initialize_session_state() -> None:
    """Initialize or reset session state variables."""
    session_state = st.session_state

    # Initialize API client
    session_state.setdefault("fpbase_client", FPbaseAPI())

    # Initialize dataframes
    fluorophore_df = load_fluorophore_data()
    session_state.setdefault("fluorophore_df", fluorophore_df)
    session_state.setdefault(
        "search_results", pd.DataFrame(columns=DEFAULT_COLUMNS)
    )

    # Initialize global parameters with plot config values
    global_params = DEFAULT_GLOBAL_PARAMS.copy()
    if "wavelength_range" in SHARED_PLOT_CONFIG:
        global_params["wavelength_range"] = SHARED_PLOT_CONFIG["wavelength_range"]
    session_state.setdefault("global_params", global_params)

    # Initialize tissue parameters from tissue_config
    session_state.setdefault("tissue_params", DEFAULT_TISSUE_PARAMS.copy())

    # Initialize laser data
    session_state.setdefault("laser_df", initialize_laser_data())
    session_state.setdefault("show_lasers", True)

    # Initialize plot configuration
    session_state.setdefault("plot_config", SHARED_PLOT_CONFIG.copy())
