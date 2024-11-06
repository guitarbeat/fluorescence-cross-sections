"""Laser model for managing laser configurations and visualization."""
import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

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
    ]
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
    
    # Initialize laser visibility and settings
    if "laser_settings" not in st.session_state:
        st.session_state.laser_settings = {
            "show_lasers": True,
            "opacity": 0.3,
            "label_size": 10,
            "position": "top",  # 'top' or 'overlay'
        }

def validate_laser_range(start: float, end: float) -> Tuple[bool, str]:
    """Validate laser wavelength range.
    
    Args:
        start: Starting wavelength in nm
        end: Ending wavelength in nm
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (700 <= start <= 2400):
        return False, f"Start wavelength {start} nm is outside valid range (700-2400 nm)"
    if not (700 <= end <= 2400):
        return False, f"End wavelength {end} nm is outside valid range (700-2400 nm)"
    if start >= end:
        return False, f"Start wavelength ({start} nm) must be less than end wavelength ({end} nm)"
    return True, ""

def update_laser_range(idx: int, start: float, end: float) -> Tuple[bool, str]:
    """Update laser range with validation.
    
    Args:
        idx: Index of laser to update
        start: New start wavelength
        end: New end wavelength
        
    Returns:
        Tuple of (success, message)
    """
    is_valid, error_msg = validate_laser_range(start, end)
    if not is_valid:
        return False, error_msg
        
    try:
        st.session_state.laser_df.loc[idx, ["Start_nm", "End_nm"]] = [start, end]
        return True, f"Updated laser range to {start}-{end} nm"
    except Exception as e:
        return False, f"Error updating laser range: {str(e)}"

def update_laser_color(idx: int, color: str) -> Tuple[bool, str]:
    """Update laser color with validation.
    
    Args:
        idx: Index of laser to update
        color: New color in hex format
        
    Returns:
        Tuple of (success, message)
    """
    try:
        st.session_state.laser_df.loc[idx, "Color"] = color
        return True, f"Updated laser color to {color}"
    except Exception as e:
        return False, f"Error updating laser color: {str(e)}"

def delete_laser(idx: int) -> Tuple[bool, str]:
    """Delete a laser with error handling.
    
    Args:
        idx: Index of laser to delete
        
    Returns:
        Tuple of (success, message)
    """
    try:
        st.session_state.laser_df = st.session_state.laser_df.drop(idx).reset_index(drop=True)
        return True, "Laser deleted successfully"
    except Exception as e:
        return False, f"Error deleting laser: {str(e)}"

def add_laser(name: str, start: float, end: float, color: str) -> Tuple[bool, str]:
    """Add a new laser with validation.
    
    Args:
        name: Name of the laser
        start: Start wavelength in nm
        end: End wavelength in nm
        color: Color in hex format
        
    Returns:
        Tuple of (success, message)
    """
    if not name:
        return False, "Laser name is required"
        
    is_valid, error_msg = validate_laser_range(start, end)
    if not is_valid:
        return False, error_msg
        
    try:
        new_laser = pd.DataFrame({
            "Name": [name], 
            "Start_nm": [start], 
            "End_nm": [end],
            "Color": [color]
        })
        st.session_state.laser_df = pd.concat(
            [st.session_state.laser_df, new_laser], 
            ignore_index=True
        )
        return True, f"Added laser: {name}"
    except Exception as e:
        return False, f"Error adding laser: {str(e)}"

def calculate_laser_positions(
    lasers: pd.DataFrame, 
    base_y: float = 1.3, 
    spacing: float = 0.03
) -> List[float]:
    """Calculate vertical positions for lasers to avoid overlap.
    
    Args:
        lasers: DataFrame containing laser data
        base_y: Base y-position for first laser
        spacing: Vertical spacing between lasers
        
    Returns:
        List of y-positions for each laser
    """
    if lasers.empty:
        return []

    # Adjust spacing based on y-axis scale
    if base_y > 100:  # For log scale (cross-section plot)
        adjusted_spacing = base_y * 0.25
        base_y = base_y * 1.2
    else:  # For linear scale (tissue plot)
        adjusted_spacing = 0.12
        base_y = 1.5

    # Sort lasers by start wavelength
    lasers = lasers.sort_values('Start_nm')
    
    # Initialize positions list and track occupied ranges
    positions: List[float] = []
    occupied_ranges: List[List[Tuple[float, float, float]]] = []
    
    for _, laser in lasers.iterrows():
        start_nm = laser['Start_nm']
        end_nm = laser['End_nm']
        
        # Find lowest available y position without overlap
        y_pos = base_y
        level = 0
        
        while True:
            if level >= len(occupied_ranges):
                occupied_ranges.append([])
                break
                
            overlap = False
            for occ_start, occ_end, _ in occupied_ranges[level]:
                if not (end_nm < occ_start or start_nm > occ_end):
                    overlap = True
                    break
            
            if not overlap:
                break
                
            level += 1
            y_pos += adjusted_spacing
        
        occupied_ranges[level].append((start_nm, end_nm, y_pos))
        positions.append(y_pos)
    
    return positions

def get_laser_settings() -> Dict[str, Any]:
    """Get current laser display settings."""
    return st.session_state.laser_settings

def update_laser_settings(settings: Dict[str, Any]) -> None:
    """Update laser display settings."""
    st.session_state.laser_settings.update(settings)
