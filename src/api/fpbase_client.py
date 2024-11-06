import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from backoff import expo, on_exception
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.api.fpbase_types import FPbaseAPIError, ProteinData

logger = logging.getLogger(__name__)


class FPbaseAPI:
    """Interface for FPbase REST API with enhanced retry logic and pagination."""

    BASE_URL: str = "https://www.fpbase.org/"
    ENDPOINTS = {
        "proteins": "api/proteins/",
        "basic": "api/proteins/basic/",
        "spectra": "api/proteins/spectra/",
        "search": "search/",
    }

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        """Initialize the FPbaseAPI instance with retry configuration."""
        self.session: requests.Session = session or self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a new session with retry configuration."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,  # wait 0.5, 1, 2... seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "FluorescenceCrossSections/1.0",
            }
        )

        return session

    @on_exception(expo, requests.exceptions.RequestException, max_tries=3)
    def _make_request(
        self, endpoint: str, params: Dict[str, Any], timeout: int = 10
    ) -> requests.Response:
        """Make an HTTP GET request with exponential backoff retry."""
        if endpoint not in self.ENDPOINTS:
            raise FPbaseAPIError(f"Invalid endpoint: {endpoint}")

        # Validate and clean parameters
        validated_params = self._validate_params(params)

        # Construct URL properly
        url = f"{self.BASE_URL.rstrip('/')}/{self.ENDPOINTS[endpoint].lstrip('/')}"

        try:
            logger.info(f"Querying FPbase API: {url} with params: {validated_params}")
            response = self.session.get(url, params=validated_params, timeout=timeout)

            if response.status_code == 404:
                logger.warning("No results found. Try adjusting your search criteria.")
                return response

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise FPbaseAPIError(f"Request failed: {str(e)}")

    def _validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean query parameters."""
        validated = params.copy()
        validated["format"] = "json"  # Ensure JSON format

        # Validate numerical parameters
        if "min_brightness" in validated:
            try:
                validated["min_brightness"] = float(validated["min_brightness"])
            except ValueError:
                logger.warning("Invalid min_brightness value, removing from query")
                validated.pop("min_brightness")

        if "wavelength_range" in validated:
            try:
                min_wave, max_wave = validated["wavelength_range"]
                validated["two_photon_peak__gte"] = float(min_wave)
                validated["two_photon_peak__lte"] = float(max_wave)
                validated.pop("wavelength_range")
            except (ValueError, TypeError):
                logger.warning("Invalid wavelength_range value, removing from query")
                validated.pop("wavelength_range")

        return validated

    def get_search_url(self, params: Dict[str, Any]) -> str:
        """Generate a human-readable search URL."""
        base = f"{self.BASE_URL}{self.ENDPOINTS['search']}"
        params_str = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base}?{params_str}"

    def search_proteins(
        self, params: Dict[str, Any], timeout: int = 10
    ) -> List[ProteinData]:
        """
        Search proteins using FPbase API with enhanced error handling.
        """
        try:
            # Use 'basic' endpoint for simpler response structure
            endpoint = "basic"

            # Generate human-readable URL for reference
            search_url = self.get_search_url(params)
            logger.info(f"Equivalent search URL: {search_url}")

            # Make request with timeout
            response = self._make_request(endpoint, params, timeout=timeout)

            # Log raw response
            logger.debug(f"Raw API Response Status: {response.status_code}")
            logger.debug(f"Raw API Response Headers: {dict(response.headers)}")
            logger.debug(f"Raw API Response Content: {response.text}")

            # Only try to parse JSON if we got a successful response
            if response.status_code == 200:
                data = response.json()

                proteins = []
                for item in data:
                    try:
                        protein = ProteinData.from_api_response(item)
                        proteins.append(protein)
                    except Exception as e:
                        logger.warning(f"Error processing protein data: {e}")
                        continue

                logger.info(f"Retrieved {len(proteins)} proteins")
                return proteins
            else:
                logger.error(
                    f"API request failed with status code: {response.status_code}"
                )
                return []

        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            logger.exception("Full traceback:")  # This will log the full stack trace
            raise FPbaseAPIError(f"Search failed: {str(e)}")

    def to_dataframe(self, proteins: List[ProteinData]) -> pd.DataFrame:
        """Convert a list of ProteinData objects to a DataFrame."""
        try:
            data = []
            for protein in proteins:
                try:
                    fpbase_url = f"{self.BASE_URL.rstrip('/')}{protein.url}"
                    row = {
                        "Name": protein.name,
                        "Em_Max": protein.default_state.em_max,
                        "Ex_Max": protein.default_state.ex_max,
                        "Reference": fpbase_url,
                        "QY": protein.default_state.qy,
                        "EC": protein.default_state.ext_coeff,
                        "pKa": protein.default_state.pka,
                        "Brightness": protein.default_state.brightness,
                        "Stokes": protein.default_state.stokes,
                        "Lifetime": protein.default_state.lifetime,
                        "Maturation": protein.default_state.maturation,
                    }
                    data.append(row)
                except AttributeError as e:
                    logger.warning(f"Error processing protein {protein.name}: {str(e)}")
                    continue

            df = pd.DataFrame(data)
            logger.info(f"Created DataFrame with {len(df)} rows")
            return df

        except Exception as e:
            logger.error(f"Error creating DataFrame: {str(e)}")
            return pd.DataFrame()
