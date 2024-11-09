from typing import Any, Dict

import pandas as pd
import streamlit as st

from src.api.fpbase_client import FPbaseAPI

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
    """Search for proteins using the FPbase API."""
    try:
        params = filters.copy()
        if query:
            params["name__icontains"] = query

        with st.spinner("🔍 Searching FPbase database..."):
            response = client._make_request("basic", params, timeout=10)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "message": "No proteins found matching your criteria.",
                }

            # Get raw data from response
            raw_data = response.json()
            
            if not raw_data:
                return {
                    "success": False,
                    "message": "No proteins found matching your criteria.",
                }

            # Convert directly to DataFrame keeping all columns
            results_df = pd.DataFrame(raw_data)
            
            # Create proper FPbase URL
            base_url = "https://www.fpbase.org"
            results_df["URL"] = base_url + results_df["url"].fillna("")
            
            # Rename some columns for clarity
            column_renames = {
                "name": "Name",
                "ex_max": "Ex λ (nm)",
                "em_max": "Em λ (nm)",
                "qy": "Quantum Yield",
                "ext_coeff": "Extinction Coeff",
                "pka": "pKa",
                "brightness": "Brightness",
                "maturation": "Maturation",
                "lifetime": "Lifetime",
                "stokes": "Stokes Shift",
                "bleach": "Photobleaching",
            }
            results_df = results_df.rename(columns=column_renames)
            
            # Add note about two-photon data
            results_df["Two-Photon Note"] = "Two-photon cross-section data not available from FPbase. See Zipfel Lab data for GM values."
            
            return {
                "success": True,
                "message": f"Found {len(results_df)} proteins. Note: Two-photon cross-section values (GM) are not available from FPbase.",
                "data": results_df
            }

    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return {"success": False, "message": f"Search failed: {str(e)}"}


def render_search_panel(key_prefix: str = "") -> None:
    """Render the simplified FPbase search panel."""
    with st.expander("🔍 FPbase Database Search", expanded=True):
        st.markdown("### Search FPbase")
        
        st.info("""
            **Note about Two-Photon Data:**
            - FPbase provides spectral shapes but not absolute cross-section values (GM units)
            - For accurate two-photon cross-sections, refer to the Zipfel Lab data
            - Use this search to find additional fluorophore properties (QY, emission, etc.)
        """)

        name_query = st.text_input(
            "Search by name",
            placeholder="e.g., GFP, RFP, YFP",
            help="Enter protein name (e.g., 'GFP', 'RFP', etc.)",
            key=f"{key_prefix}name_query"
        )

        if st.button("🔍 Search", use_container_width=True, type="primary", key=f"{key_prefix}search_button"):
            result = search_proteins(name_query, {"name__icontains": name_query}, st.session_state.fpbase_client)

            if result["success"]:
                # Show all columns in the results table with clickable URLs
                st.data_editor(
                    result["data"],
                    num_rows="dynamic",
                    column_config={
                        "URL": st.column_config.LinkColumn(
                            "FPbase Link",
                            display_text="View on FPbase",  # Text to show for the link
                            help="Click to view on FPbase website"
                        ),
                        "Name": st.column_config.TextColumn("Name"),
                        "Ex λ (nm)": st.column_config.NumberColumn(format="%d"),
                        "Em λ (nm)": st.column_config.NumberColumn(format="%d"),
                        "Quantum Yield": st.column_config.NumberColumn(format="%.2f"),
                        "Extinction Coeff": st.column_config.NumberColumn(format="%d"),
                        "pKa": st.column_config.NumberColumn(format="%.1f"),
                        "Brightness": st.column_config.NumberColumn(format="%.1f"),
                        "Maturation": st.column_config.NumberColumn(format="%.1f"),
                        "Lifetime": st.column_config.NumberColumn(format="%.1f"),
                        "Stokes Shift": st.column_config.NumberColumn(format="%.1f"),
                        "Photobleaching": st.column_config.NumberColumn(format="%.1f"),
                    },
                    use_container_width=True,
                    hide_index=True,
                    key=f"{key_prefix}search_editor"
                )
            else:
                st.warning(result["message"])
