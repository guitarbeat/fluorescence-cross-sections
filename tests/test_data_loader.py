import os
import sys

import pytest
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.data_loader import (
    load_water_absorption_data,
    load_fluorophore_data,
)


def test_load_water_absorption_data_returns_dataframe():
    """Water absorption loader should return a populated DataFrame."""
    df = load_water_absorption_data()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"wavelength", "absorption"}.issubset(df.columns)


def test_load_fluorophore_data_returns_dataframe():
    """Fluorophore loader should return a populated DataFrame with expected columns."""
    df = load_fluorophore_data()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {
        "Name",
        "Wavelength",
        "Cross_Section",
        "Reference",
        "Em_Max",
        "QY",
        "EC",
        "pKa",
    }
    assert expected_cols.issubset(df.columns)

# Add more tests for other functions and edge cases

