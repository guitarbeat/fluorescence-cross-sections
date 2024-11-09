import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProteinState:
    """Represents fluorescence-related properties of a protein's state."""

    ex_max: Optional[float]
    em_max: Optional[float]
    qy: Optional[float]
    ext_coeff: Optional[float]
    pka: Optional[float]
    brightness: Optional[float]
    stokes: Optional[float]
    lifetime: Optional[float]
    maturation: Optional[float]
    bleach: Optional[float]

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ProteinState":
        """Create a ProteinState instance with validated data."""

        def safe_float(value: Any, field_name: str) -> Optional[float]:
            if value is None or value == "":  # Handle empty strings
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                logger.warning(f"Invalid {field_name} value: {value}")
                return None

        return cls(
            ex_max=safe_float(data.get("ex_max"), "ex_max"),
            em_max=safe_float(data.get("em_max"), "em_max"),
            qy=safe_float(data.get("qy"), "qy"),
            ext_coeff=safe_float(data.get("ext_coeff"), "ext_coeff"),
            pka=safe_float(data.get("pka"), "pka"),
            brightness=safe_float(data.get("brightness"), "brightness"),
            stokes=safe_float(data.get("stokes"), "stokes"),
            lifetime=safe_float(data.get("lifetime"), "lifetime"),
            maturation=safe_float(data.get("maturation"), "maturation"),
            bleach=safe_float(data.get("bleach"), "bleach"),
        )


@dataclass
class ProteinData:
    """Stores information about a fluorescent protein."""

    name: str
    url: str
    slug: str
    default_state: ProteinState

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "ProteinData":
        """Create a ProteinData instance from API response."""
        if not data.get("name"):
            logger.warning("Missing protein name in API response")
            name = "Unknown Protein"
        else:
            name = str(data["name"])

        state = ProteinState.from_api_response(data)

        return cls(
            name=name,
            url=data.get("url", ""),
            slug=data.get("slug", "").lower(),
            default_state=state,
        )


class FPbaseAPIError(Exception):
    """Custom exception for FPbase API errors."""
