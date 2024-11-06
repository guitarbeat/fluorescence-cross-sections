import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd

from src.models.tissue_config import DEFAULT_TISSUE_PARAMS

logger = logging.getLogger(__name__)



def load_water_absorption_data() -> pd.DataFrame:
    """Load water absorption data from kou93b.dat"""
    data_path = Path(__file__).parent.parent.parent / "data" / "kou93b.dat"
    try:
        # Try reading with different encodings and skip the header properly
        df = pd.read_csv(
            data_path,
            delim_whitespace=True,  # Skip the header rows
            skiprows=6,
            names=["wavelength", "absorption"],
            encoding="latin1",  # Use latin1 encoding instead of utf-8
            comment="#",  # Skip any comment lines
        )
        # Flip the data as in the MATLAB code
        return df.iloc[::-1].reset_index(drop=True)
    except Exception as e:
        print(f"Error loading water absorption data: {e}")
        # Return a minimal dataset if loading fails
        return pd.DataFrame(
            {"wavelength": np.linspace(800, 2400, 1000), "absorption": np.zeros(1000)}
        )


def calculate_two_photon_wavelength(lambda_a: float, lambda_b: float) -> float:
    """Calculate the effective two-photon excitation wavelength."""
    # Round to nearest 5nm as in MATLAB code
    return round((2 / ((1 / lambda_a) + (1 / lambda_b))) / 5) * 5


def calculate_tissue_parameters(
    wavelengths: npt.NDArray[np.float64],
    g: float = DEFAULT_TISSUE_PARAMS["g"],
    a: float = DEFAULT_TISSUE_PARAMS["a"],
    water_content: float = DEFAULT_TISSUE_PARAMS["water_content"],
    b: float = DEFAULT_TISSUE_PARAMS["b"],
    depth: float = DEFAULT_TISSUE_PARAMS["depth"],
    normalization_wavelength: float = DEFAULT_TISSUE_PARAMS["normalization_wavelength"],
    lambda_a: Optional[float] = None,
    lambda_b: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate tissue penetration parameters using experimental data."""
    try:
        # Load water absorption data
        water_data = load_water_absorption_data()

        # Interpolate water absorption to match wavelengths
        mua = np.interp(wavelengths, water_data["wavelength"], water_data["absorption"])
        mua = mua * water_content / 10  # Scale by water content and convert units

        # Calculate scattering coefficient
        mus_prime = a * (wavelengths / 500) ** (-b)
        mus = mus_prime / (1 - g)

        # Calculate total attenuation
        total_mu = mus + mua

        # Calculate transmission and normalize
        T = np.exp(-total_mu * depth)
        norm_idx = np.abs(wavelengths - normalization_wavelength).argmin()
        T = T / T[norm_idx]  # Normalize at specified wavelength

        # Calculate water absorption percentage
        Tw = 1 - np.exp(-mua * depth)  # Match MATLAB calculation

        # Find wavelength with maximum transmission
        max_trans_wavelength = wavelengths[np.argmax(T)]

        # Calculate depth-dependent parameters
        z_range = np.arange(0, 2.1, 0.1)  # 0 to 2mm in 0.1mm steps
        T_z = np.zeros((len(z_range), len(wavelengths)))
        Tw_z = np.zeros((len(z_range), len(wavelengths)))

        for i, z in enumerate(z_range):
            T_z[i] = np.exp(-(mua + mus) * z)
            T_z[i] = T_z[i] / T_z[i, norm_idx]  # Normalize at each depth
            Tw_z[i] = 1 - np.exp(-mua * z)

        # Two-photon comparison if wavelengths provided
        two_photon_data = None
        if lambda_a is not None and lambda_b is not None:
            lambda_c = calculate_two_photon_wavelength(lambda_a, lambda_b)
            # Get values at specific wavelengths
            idx_a = np.abs(wavelengths - lambda_a).argmin()
            idx_b = np.abs(wavelengths - lambda_b).argmin()
            idx_c = np.abs(wavelengths - lambda_c).argmin()

            two_photon_data = {
                "wavelengths": [lambda_a, lambda_b, lambda_c],
                "T": [T[idx_a], T[idx_b], T[idx_c]],
                "Tw": [Tw[idx_a], Tw[idx_b], Tw[idx_c]],
            }

        return {
            "T": T,
            "Tw": Tw,
            "T_z": T_z,
            "Tw_z": Tw_z,
            "z_range": z_range,
            "max_transmission_wavelength": max_trans_wavelength,
            "two_photon_data": two_photon_data,
        }

    except Exception as e:
        logger.error(f"Error calculating tissue parameters: {e}")
        return {}
