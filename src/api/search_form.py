from typing import Any, Dict

import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI, FPbaseAPIError


def create_search_filters() -> Dict[str, Any]:
    """Create focused search filters for fluorophore exploration."""
    filters = {}

    with st.expander("Spectral Filters"):
        col1, col2 = st.columns(2)

        with col1:
            # Emission range
            em_min, em_max = st.slider(
                "Emission Range (nm)",
                min_value=350,
                max_value=800,
                value=(450, 550),
                help="Filter by emission maximum wavelength",
            )
            filters["em_max__range"] = f"{em_min},{em_max}"

            # Quantum yield
            min_qy = st.number_input(
                "Minimum Quantum Yield",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                help="Filter by minimum quantum yield",
            )
            if min_qy > 0:
                filters["qy__gte"] = min_qy

        with col2:
            # Brightness filter
            min_brightness = st.number_input(
                "Minimum Brightness",
                min_value=0.0,
                value=0.0,
                help="Filter by minimum brightness (QY × EC / 1000)",
            )
            if min_brightness > 0:
                filters["brightness__gte"] = min_brightness

    return filters


def download_results(df: pd.DataFrame) -> None:
    """Add download button for search results."""
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="fpbase_search_results.csv",
            mime="text/csv",
        )


def search_proteins(
    query: str, filters: Dict[str, Any], client: FPbaseAPI
) -> Dict[str, Any]:
    """
    Search for proteins using the FPbase API with advanced filters.

    Args:
        query (str): The search query string.
        filters (Dict[str, Any]): Additional search filters.
        client (FPbaseAPI): An instance of the FPbase API client.

    Returns:
        Dict[str, Any]: A dictionary containing search results and status.
    """
    try:
        # Combine name query with filters
        params = filters.copy()
        if query:
            params["name__icontains"] = query

        with st.spinner("🔍 Searching FPbase database..."):
            # Get raw response first
            response = client._make_request("basic", params, timeout=10)

            if response.status_code == 200:
                # Show the raw JSON response for the first result
                raw_data = response.json()
                if raw_data:
                    st.write("### Example API Response (First Result):")
                    st.json(raw_data[0])  # Show first result in pretty format

            # Continue with normal processing
            proteins = client.search_proteins(params, timeout=10)

            if not proteins:
                return {
                    "success": False,
                    "message": "No proteins found matching your criteria.",
                }

            results_df = client.to_dataframe(proteins)

            # Show all results, even those without complete data
            if results_df.empty:
                return {"success": False, "message": "No proteins found."}

            # Format message to indicate total proteins and those with complete data
            total_proteins = len(results_df)
            complete_data = len(
                results_df.dropna(subset=["Em_Max"])
            )  # Only check for emission data

            message = (
                f"Found {total_proteins} proteins total. "
                f"{complete_data} have complete emission data. "
                "Click the URLs to view protein details on FPbase."
            )

            return {"success": True, "message": message, "data": results_df}

    except FPbaseAPIError as e:
        return {"success": False, "message": f"Search failed: {str(e)}"}


def render_search_panel() -> None:
    """Render the enhanced FPbase search panel."""
    st.markdown("### FPbase Search")

    # Basic search with name
    name_query = st.text_input(
        "Search by name",
        placeholder="e.g., GFP, RFP, YFP",
        help="Enter protein name (e.g., 'GFP', 'RFP', etc.)",
    )

    # Convert to API parameter
    filters = {"name__icontains": name_query} if name_query else {}

    # Get spectral filters
    filters.update(create_search_filters())

    # Search button
    if st.button("🔍 Search", use_container_width=True, type="primary"):
        result = search_proteins(name_query, filters, st.session_state.fpbase_client)

        if result["success"]:
            st.success(result["message"])

            # Display results in a tabbed interface
            tab1, tab2 = st.tabs(["Table View", "Summary Stats"])

            with tab1:
                # Display results table
                st.dataframe(
                    result["data"],
                    column_config={
                        "Reference": st.column_config.LinkColumn("FPbase Link")
                    },
                    use_container_width=True,
                    height=400,
                )

                # Download button
                download_results(result["data"])

            with tab2:
                # Show focused summary statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Proteins", len(result["data"]))
                    if "Brightness" in result["data"].columns:
                        st.metric(
                            "Average Brightness",
                            f"{result['data']['Brightness'].mean():.2f}",
                        )
                with col2:
                    st.metric(
                        "With Emission Data", result["data"]["Em_Max"].notna().sum()
                    )
                    if "QY" in result["data"].columns:
                        st.metric("Average QY", f"{result['data']['QY'].mean():.2f}")
        else:
            st.warning(result["message"])
