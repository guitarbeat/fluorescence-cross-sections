"""Laser model for managing laser configurations and visualization."""

from typing import Dict, List

import pandas as pd
import streamlit as st

# Default laser configurations
DEFAULT_LASERS: Dict[str, List] = {
    "Name": ["Ti:Sapphire", "Yb fiber", "2C2P", "Diamond", "Er fiber", "OPO/OPA"],
    "Range": [
        (800, 1000),
        (1050, 1070),
        (1150, 1200),
        (1250, 1300),
        (1550, 1600),
        (1100, 2200),
    ],
    "Color": [
        "#ff4b4b",  # Red
        "#4b4bff",  # Blue
        "#37c463",  # Green
        "#ff9d42",  # Orange
        "#42fff9",  # Cyan
        "#f942ff",  # Magenta
    ],
}


def initialize_laser_data() -> None:
    """Initialize laser data in session state with validation."""
    if "laser_df" not in st.session_state:
        data = {
            "Name": DEFAULT_LASERS["Name"],
            "Start_nm": [r[0] for r in DEFAULT_LASERS["Range"]],
            "End_nm": [r[1] for r in DEFAULT_LASERS["Range"]],
            "Color": DEFAULT_LASERS["Color"],
        }
        st.session_state.laser_df = pd.DataFrame(data)



def add_laser(name: str, start_nm: float, end_nm: float, color: str) -> bool:
    """Add a new laser to the session state.
    
    Args:
        name: Name of the laser
        start_nm: Starting wavelength in nm
        end_nm: Ending wavelength in nm
        color: Color in hex format
        
    Returns:
        bool: True if laser was added successfully, False otherwise
    """
    if not name:
        return False
        
    try:
        new_laser = pd.DataFrame({
            "Name": [name],
            "Start_nm": [start_nm],
            "End_nm": [end_nm],
            "Color": [color]
        })
        
        if "laser_df" not in st.session_state:
            initialize_laser_data()
            
        st.session_state.laser_df = pd.concat(
            [st.session_state.laser_df, new_laser],
            ignore_index=True
        )
        return True
        
    except Exception as e:
        st.error(f"Error adding laser: {str(e)}")
        return False
