"""Constants and configuration values for the Deep Tissue Imaging Optimizer."""

from pathlib import Path

# Project directories
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

# Common file paths
FLUOROPHORE_CSV = DATA_DIR / "fluorophores.csv"
LASER_CSV = DATA_DIR / "lasers.csv"

# Column definitions
FLUOROPHORE_COLUMNS = [
    "Name", "Wavelength", "Cross_Section", "Reference",
    "Em_Max", "Ex_Max", "QY", "EC", "pKa", "Brightness",
]

# Basic columns used for search results
BASIC_FLUOROPHORE_COLUMNS = [
    "Name", "Wavelength", "Cross_Section", "Reference",
]

# Tissue depth slider configuration
TISSUE_DEPTH_SLIDER_CONFIG = {
    "min_value": 0.1,
    "max_value": 10.0,
    "step": 0.1,
    "help": "Depth of tissue penetration in millimeters"
}

__all__ = [
    "ROOT_DIR",
    "DATA_DIR",
    "FLUOROPHORE_CSV",
    "LASER_CSV",
    "FLUOROPHORE_COLUMNS",
    "BASIC_FLUOROPHORE_COLUMNS",
]
