import logging
import numpy as np
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

def load_water_absorption_data() -> pd.DataFrame:
    """Load water absorption data from kou93b.dat."""
    data_path = Path(__file__).parent.parent.parent / "data" / "kou93b.dat"
    try:
        df = pd.read_csv(
            data_path,
            delim_whitespace=True,
            skiprows=6,
            names=["wavelength", "absorption"],
            encoding="latin1",
            comment="#",
        )
        # Flip the data as in the MATLAB code
        df = df.iloc[::-1].reset_index(drop=True)
        return df
    except Exception as e:
        logger.error(f"Error loading water absorption data: {e}")
        # Return a minimal dataset if loading fails
        return pd.DataFrame(
            {
                "wavelength": np.linspace(800, 2400, 1000),
                "absorption": np.zeros(1000),
            }
        )