"""Service layer for fluorophore data management and operations."""

import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

from src.config.constants import FLUOROPHORE_COLUMNS, FLUOROPHORE_CSV

logger = logging.getLogger(__name__)


class FluorophoreService:
    """Service class for fluorophore data operations."""

    @staticmethod
    def get_fluorophore_visibility(df: pd.DataFrame) -> Dict[str, bool]:
        """Get fluorophore visibility settings from session state or initialize defaults."""
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
        """
        Save fluorophore data to session state and external storage.

        Args:
            edited_df: DataFrame with edited fluorophore data

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Remove visibility column before saving
            save_df = edited_df.drop(columns=["Visible"])

            # Update session state
            st.session_state.fluorophore_df = save_df

            # Send to external storage
            data = save_df.to_dict("records")
            # The following lines were removed as per the edit hint:
            # send_data("fluorophores", data)

            # Save to CSV
            save_df.to_csv(FLUOROPHORE_CSV, index=False)

            logger.info("Fluorophore data saved successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to save fluorophore data: {e}")
            return False




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
