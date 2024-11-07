from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st

# Constants
DATA_PATH = Path("data/fluorophores.csv")
DEFAULT_COLUMNS = [
    "Name", "Wavelength", "Cross_Section", "Reference",  # Core plotting data
    "Em_Max", "Ex_Max", "QY", "EC", "pKa", "Brightness"  # Additional properties
]

class FluorophoreManager:
    def __init__(self):
        if "fluorophore_df" not in st.session_state:
            st.session_state.fluorophore_df = pd.DataFrame(columns=DEFAULT_COLUMNS)

    @staticmethod
    def get_column_config() -> Dict[str, Any]:
        """Column configurations for the data editor."""
        return {
            "Name": st.column_config.TextColumn(
                "Fluorophore", help="Protein name", required=True
            ),
            "Wavelength": st.column_config.NumberColumn(
                "2P λ (nm)", help="Two-photon excitation wavelength", format="%d", required=True
            ),
            "Cross_Section": st.column_config.NumberColumn(
                "Cross Section (GM)", help="Two-photon cross section (GM)", format="%.1f"
            ),
            "Reference": st.column_config.TextColumn(
                "Reference", help="Citation or link to source"
            ),
            "Em_Max": st.column_config.NumberColumn(
                "Em λ (nm)", help="Peak emission wavelength", format="%d"
            ),
            "Ex_Max": st.column_config.NumberColumn(
                "Ex λ (nm)", help="Peak excitation wavelength", format="%d"
            ),
            "QY": st.column_config.NumberColumn(
                "QY", help="Quantum yield", min_value=0, max_value=1, format="%.2f"
            ),
            "EC": st.column_config.NumberColumn(
                "EC (M⁻¹cm⁻¹)", help="Extinction coefficient", format="%d"
            ),
            "Brightness": st.column_config.NumberColumn(
                "Brightness", help="EC × QY / 1000", format="%.2f", disabled=True
            ),
            "pKa": st.column_config.NumberColumn(
                "pKa", help="pH at 50% fluorescence", format="%.1f"
            ),
        }

    def save_data(self, df: pd.DataFrame) -> None:
        """Save and validate fluorophore data."""
        try:
            if df["Name"].isna().any():
                raise ValueError("All fluorophores must have a name")
            
            # Calculate brightness
            df["Brightness"] = (df["EC"] * df["QY"] / 1000).round(2)
            
            # Save to file
            DATA_PATH.parent.mkdir(exist_ok=True)
            df.to_csv(DATA_PATH, index=False)
            st.session_state.fluorophore_df = df
            
        except Exception as e:
            st.error(f"Failed to save data: {str(e)}")
            raise

    def render_editor(self) -> None:
        """Render the fluorophore editor interface."""
        edited_df = st.data_editor(
            st.session_state.fluorophore_df,
            num_rows="dynamic",
            column_config=self.get_column_config(),
            hide_index=True,
            key="fluorophore_editor",
            use_container_width=True,
            height=400,
            column_order=DEFAULT_COLUMNS,
            disabled=["Brightness"],
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                with st.status("Saving changes...") as status:
                    try:
                        self.save_data(edited_df)
                        status.update(label="✅ Saved", state="complete")
                        st.rerun()
                    except Exception:
                        status.update(label="Failed to save", state="error")

        with col2:
            if st.button("📥 Import Selected", use_container_width=True):
                self._handle_import()

        # FPbase viewer
        with st.expander("📚 FPbase Resources", expanded=False):
            st.markdown(
                """
                - [Spectra Viewer](https://www.fpbase.org/spectra/)
                - [Activity Charts](https://www.fpbase.org/activity/)
                - [Popular Proteins](https://www.fpbase.org/proteins/)
                """
            )
            st.components.v1.iframe(
                src="https://www.fpbase.org/spectra/?embed=true",
                height=600,
                scrolling=False
            )

    def _handle_import(self) -> None:
        """Handle importing fluorophores from search results."""
        if "search_results" not in st.session_state or st.session_state.search_results.empty:
            st.info("No search results available")
            return

        with st.form("select_proteins", clear_on_submit=True):
            st.write("Select proteins to import:")
            selected = {
                idx: st.checkbox(f"{row['Name']} (Em: {row['Em_Max']}nm)")
                for idx, row in st.session_state.search_results.iterrows()
            }

            if st.form_submit_button("Import"):
                selected_df = st.session_state.search_results[
                    [selected[idx] for idx in selected.keys()]
                ]
                
                if not selected_df.empty:
                    with st.status("Importing...") as status:
                        try:
                            selected_df["Reference"] = "FPbase"
                            new_df = pd.concat(
                                [st.session_state.fluorophore_df, selected_df],
                                ignore_index=True
                            ).drop_duplicates(subset=["Name"], keep="last")
                            
                            self.save_data(new_df)
                            status.update(label="✅ Imported", state="complete")
                            st.rerun()
                        except Exception as e:
                            status.update(label=f"Import failed: {e}", state="error")
                else:
                    st.warning("No proteins selected")

def render_fluorophore_manager():
    """Main entry point."""
    manager = FluorophoreManager()
    manager.render_editor()
