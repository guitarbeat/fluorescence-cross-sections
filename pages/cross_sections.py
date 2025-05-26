"""Cross-sections Analysis Page"""
import streamlit as st
import pandas as pd
from typing import Optional
from src.plots.cross_section_plot import (create_cross_section_plot,
                                          get_marker_settings,
                                          marker_settings_ui)
from src.api.google import send_data


def render_cross_sections_plot(df: Optional[pd.DataFrame] = None) -> None:
    """Render cross-sections plot with data table."""
    if df is not None and not df.empty:
        # Get or initialize visibility settings in session state
        if "fluorophore_visibility" not in st.session_state:
            st.session_state.fluorophore_visibility = {
                row["Name"]: True for _, row in df.iterrows()
            }

        # Add visibility column to the DataFrame
        df_with_visibility = df.copy()
        df_with_visibility["Visible"] = df_with_visibility["Name"].map(
            st.session_state.fluorophore_visibility
        ).fillna(True)

        # Create filtered dataframe based on visibility
        visible_df = df_with_visibility[df_with_visibility["Visible"]]

        # Get parameters from session state
        global_params = st.session_state.global_params
        tissue_params = st.session_state.tissue_params
        depth = tissue_params.get("depth", 1.0)
        norm_wavelength = global_params["normalization_wavelength"]
        wavelength_range = global_params["wavelength_range"]
        absorption_threshold = global_params["absorption_threshold"]

        # Plot with visible fluorophores only
        markers_dict = get_marker_settings()
        fig = create_cross_section_plot(
            visible_df[["Name", "Wavelength", "Cross_Section", "Reference"]],
            markers_dict=markers_dict,
            normalization_wavelength=norm_wavelength,
            depth=depth,
            wavelength_range=wavelength_range,
            absorption_threshold=absorption_threshold,
        )

        # Display plot
        st.plotly_chart(
            fig,
            use_container_width=True,
            theme="streamlit",
            config={
                'displayModeBar': True,
                'responsive': True
            }
        )
    else:
        st.info("No data to display - try searching for fluorophores.")

    # Marker settings in a popover
    with st.popover("Marker Settings"):
        marker_settings_ui()


# Main cross-sections analysis page
st.header("📈 Cross-sections Analysis")
st.caption("View and compare two-photon cross-sections of different fluorophores")

# Direct container with border for better visual separation
plot_container = st.container(border=True)
with plot_container:
    render_cross_sections_plot(st.session_state.get("fluorophore_df"))

# Add the table with visibility toggles
st.markdown("### Fluorophore Data")
if "fluorophore_df" in st.session_state:
    # Add Hide/Show All toggle
    show_all = st.toggle(
        "Show All Fluorophores",
        value=True,
        key="show_all_fluorophores"
    )

    # Add visibility column to the editor
    df_for_editor = st.session_state.fluorophore_df.copy()

    # Update all visibility states if show_all changes
    if show_all:
        st.session_state.fluorophore_visibility = {
            name: True for name in df_for_editor["Name"]
        }
    else:
        st.session_state.fluorophore_visibility = {
            name: False for name in df_for_editor["Name"]
        }

    df_for_editor["Visible"] = df_for_editor["Name"].map(
        st.session_state.fluorophore_visibility
    ).fillna(True)

    edited_df = st.data_editor(
        df_for_editor,
        num_rows="dynamic",
        column_config={
            "Visible": st.column_config.CheckboxColumn(
                "Show",
                help="Toggle fluorophore visibility in plot",
                default=True,
            ),
            "Name": st.column_config.TextColumn(
                "Fluorophore",
                help="Fluorophore name",
            ),
            "Wavelength": st.column_config.NumberColumn(
                "2P λ (nm)",
                help="Two-photon excitation wavelength",
                format="%d"
            ),
            "Cross_Section": st.column_config.NumberColumn(
                "Cross Section (GM)",
                help="Two-photon cross section in Goeppert-Mayer units",
                format="%.2f"
            ),
            "Reference": st.column_config.TextColumn(
                "Reference",
                help="Data source (Zipfel Lab or FPbase)"
            ),
        },
        column_order=["Visible", "Name", "Wavelength",
                      "Cross_Section", "Reference"],
        use_container_width=True,
        hide_index=True,
        key="overview_editor"
    )

    # Update visibility settings from edited dataframe
    st.session_state.fluorophore_visibility = {
        row["Name"]: row["Visible"]
        for _, row in edited_df.iterrows()
    }

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Changes", icon="💾", type="primary", key="overview_save"):
            try:
                # Remove visibility column before saving
                save_df = edited_df.drop(columns=["Visible"])
                st.session_state.fluorophore_df = save_df

                # Save to Google Sheets
                data = save_df.to_dict('records')
                send_data("fluorophores", data)

                # Backup to CSV
                save_df.to_csv("data/fluorophores.csv", index=False)

                st.success("Changes saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save changes: {str(e)}")

    with col2:
        # Download button (without visibility column)
        csv = edited_df.drop(columns=["Visible"]).to_csv(index=False)
        st.download_button(
            label="Download Table",
            icon="📥",
            data=csv,
            file_name="fluorophore_table.csv",
            mime="text/csv",
            key="overview_download"
        )
else:
    st.info("No data in fluorophore table yet. Add fluorophores from the Fluorophore Library page.")
