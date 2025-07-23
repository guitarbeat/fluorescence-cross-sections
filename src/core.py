"""Core functionality consolidating services, state management, and common operations."""

import logging
from typing import Dict, Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI
from src.components.laser_manager import initialize_laser_data
from src.config import (
    BASIC_FLUOROPHORE_COLUMNS, 
    DEFAULT_GLOBAL_PARAMS, 
    DEFAULT_TISSUE_PARAMS,
    FLUOROPHORE_CSV,
    SHARED_PLOT_CONFIG
)
from src.utils.data_loader import load_cross_section_data, load_fluorophore_data

logger = logging.getLogger(__name__)

# Session State Management
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

    # Initialize dataframes
    session_state.setdefault("fluorophore_df", load_fluorophore_data())
    session_state.setdefault("search_results", pd.DataFrame(columns=BASIC_FLUOROPHORE_COLUMNS))

    # Initialize parameters
    session_state.setdefault("global_params", DEFAULT_GLOBAL_PARAMS.copy())
    session_state.setdefault("tissue_params", DEFAULT_TISSUE_PARAMS.copy())

    # Initialize laser data
    session_state.setdefault("laser_df", initialize_laser_data())
    session_state.setdefault("show_lasers", True)

    # Initialize plot configuration
    session_state.setdefault("plot_config", SHARED_PLOT_CONFIG.copy())

def compile_fluorophore_data(cross_sections: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Compile peak wavelengths and statistics into a single DataFrame."""
    data = []
    for name, df in cross_sections.items():
        stats = {'Name': name}
        if name == "IntrinsicFluorophores":
            for col in ["riboflavin", "folic_acid", "cholecalciferol", "retinol"]:
                peak_idx = df[col].idxmax()
                stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
                stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
        elif name == "NADH-ProteinBound":
            for col in ["gm_mean", "gm_mdh", "gm_ad"]:
                peak_idx = df[col].idxmax()
                stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
                stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
        else:
            cross_section_col = "cross_section" if "cross_section" in df.columns else df.columns[1]
            peak_idx = df[cross_section_col].idxmax()
            stats["peak_wavelength"] = df.loc[peak_idx, "wavelength"]
            stats["peak_cross_section"] = df.loc[peak_idx, cross_section_col]
        data.append(stats)
    return pd.DataFrame(data)

# Fluorophore Service
class FluorophoreService:
    """Service class for fluorophore data operations."""

    @staticmethod
    def get_fluorophore_visibility(df: pd.DataFrame) -> Dict[str, bool]:
        """Get fluorophore visibility settings from session state."""
        if "fluorophore_visibility" not in st.session_state:
            st.session_state.fluorophore_visibility = {
                row["Name"]: True for _, row in df.iterrows()
            }
        return st.session_state.fluorophore_visibility

    @staticmethod
    def update_fluorophore_visibility(df: pd.DataFrame, show_all: bool = True) -> Dict[str, bool]:
        """Update fluorophore visibility based on show_all toggle."""
        visibility = (
            {name: True for name in df["Name"]}
            if show_all
            else {name: False for name in df["Name"]}
        )
        st.session_state.fluorophore_visibility = visibility
        return visibility

    @staticmethod
    def prepare_data_for_editor(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for data editor with visibility column."""
        df_with_visibility = df.copy()
        visibility = FluorophoreService.get_fluorophore_visibility(df)
        df_with_visibility["Visible"] = df_with_visibility["Name"].map(visibility).fillna(True)
        return df_with_visibility

    @staticmethod
    def get_visible_fluorophores(df: pd.DataFrame) -> pd.DataFrame:
        """Get only visible fluorophores for plotting."""
        df_with_visibility = FluorophoreService.prepare_data_for_editor(df)
        return df_with_visibility[df_with_visibility["Visible"]]

    @staticmethod
    def update_visibility_from_editor(edited_df: pd.DataFrame) -> None:
        """Update visibility settings from edited DataFrame."""
        st.session_state.fluorophore_visibility = {
            row["Name"]: row["Visible"] for _, row in edited_df.iterrows()
        }

    @staticmethod
    def save_fluorophore_data(edited_df: pd.DataFrame) -> bool:
        """Save fluorophore data to session state and external storage."""
        try:
            save_df = edited_df.drop(columns=["Visible"])
            st.session_state.fluorophore_df = save_df
            save_df.to_csv(FLUOROPHORE_CSV, index=False)
            logger.info("Fluorophore data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to save fluorophore data: {e}")
            return False

# Plot Data Service
class PlotDataService:
    """Service class for plot data preparation."""

    @staticmethod
    def prepare_cross_section_plot_data(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for cross-section plotting."""
        if df is None or df.empty:
            return pd.DataFrame()
        visible_df = FluorophoreService.get_visible_fluorophores(df)
        return visible_df[["Name", "Wavelength", "Cross_Section", "Reference"]]

    @staticmethod
    def get_plot_parameters() -> Dict:
        """Get current plot parameters from session state."""
        return {
            "normalization_wavelength": st.session_state.global_params["normalization_wavelength"],
            "wavelength_range": st.session_state.global_params["wavelength_range"],
            "absorption_threshold": st.session_state.global_params["absorption_threshold"],
            "depth": st.session_state.tissue_params.get("depth", 1.0),
        }

# Cached data functions
@st.cache_data(ttl=300)
def get_cached_tissue_data(wavelengths: np.ndarray, depth: float, norm_wavelength: float) -> dict:
    """Cache tissue calculations to improve performance."""
    from src.plots.tissue_view import calculate_tissue_parameters
    return calculate_tissue_parameters(
        wavelengths=wavelengths,
        depth=depth,
        normalization_wavelength=norm_wavelength,
    )