
import pandas as pd
import streamlit as st


def render_results_panel() -> None:
    """Render the search results panel with enhanced layout."""
    panel_id = st.session_state.get("active_panel_id", "main")

    if "fluorophore_df" not in st.session_state:
        st.session_state.fluorophore_df = pd.DataFrame(
            columns=[
                "Name",
                "Em_Max",
                "Cross_Section",
                "Reference",
                "Ex_Max",
                "QY",
                "EC",
                "pKa",
                "Brightness",
            ]
        )

    # Main database interface
    with st.container():
        # Action buttons in a clean row
        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "📥 Import Selected",
                key=f"import_btn_{panel_id}",
                use_container_width=True,
                help="Import selected search results into database",
            ):
                if (
                    "search_results" in st.session_state
                    and not st.session_state.search_results.empty
                ):
                    with st.form("select_proteins"):
                        st.write("Select proteins to import:")
                        selected = {}
                        for idx, row in st.session_state.search_results.iterrows():
                            selected[idx] = st.checkbox(
                                f"{row['Name']} (Em: {row['Em_Max']}nm)",
                                key=f"select_{idx}",
                            )

                        if st.form_submit_button("Import Selected"):
                            selected_df = st.session_state.search_results[
                                [selected[idx] for idx in selected.keys()]
                            ]
                            if not selected_df.empty:
                                with st.spinner("Importing selected results..."):
                                    # Add reference as "FPbase" for imported data
                                    selected_df["Reference"] = "FPbase"
                                    new_df = pd.concat(
                                        [st.session_state.fluorophore_df, selected_df],
                                        ignore_index=True,
                                    ).drop_duplicates(subset=["Name"], keep="last")
                                    new_df.to_csv("data/fluorophores.csv", index=False)
                                    st.session_state.fluorophore_df = new_df
                                    st.success("Selected results imported")
                                    st.rerun()

        # Data editor with enhanced styling
        edited_df = st.data_editor(
            st.session_state.fluorophore_df,
            num_rows="dynamic",
            column_config={
                "Name": st.column_config.TextColumn(
                    "Fluorophore",
                    help="Protein name",
                    required=True,
                ),
                "Em_Max": st.column_config.NumberColumn(
                    "Em λ (nm)",
                    help="Peak emission wavelength",
                    min_value=0,
                    max_value=1000,
                    step=1,
                    format="%d",
                ),
                "Ex_Max": st.column_config.NumberColumn(
                    "Ex λ (nm)",
                    help="Peak excitation wavelength",
                    min_value=0,
                    max_value=1000,
                    step=1,
                    format="%d",
                ),
                "Cross_Section": st.column_config.NumberColumn(
                    "Cross Section (GM)",
                    help="Two-photon cross section in Göppert-Mayer units",
                    min_value=0,
                    format="%.1f",
                ),
                "Reference": st.column_config.LinkColumn(
                    "FPbase Link",
                    help="Click to view on FPbase",
                    width="medium",
                ),
                "EC": st.column_config.NumberColumn(
                    "EC (M⁻¹cm⁻¹)",
                    help="Extinction coefficient",
                    format="%d",
                ),
                "QY": st.column_config.NumberColumn(
                    "QY",
                    help="Quantum yield",
                    min_value=0,
                    max_value=1,
                    format="%.2f",
                ),
                "Brightness": st.column_config.NumberColumn(
                    "Brightness",
                    help="Relative brightness (EC × QY / 1000)",
                    format="%.2f",
                ),
                "pKa": st.column_config.NumberColumn(
                    "pKa",
                    help="pH at which fluorescence is 50% of maximum",
                    format="%.1f",
                ),
            },
            hide_index=True,
            key=f"fluorophore_editor_{panel_id}",
            use_container_width=True,
            height=300,
        )

        # Save button
        if st.button(
            "💾 Save Changes",
            key=f"save_btn_{panel_id}",
            type="primary",
            use_container_width=True,
            help="Save changes to database",
        ):
            with st.spinner("Saving changes..."):
                if edited_df["Name"].isna().any():
                    st.error("❌ All fluorophores must have a name")
                    return
                edited_df.to_csv("data/fluorophores.csv", index=False)
                st.session_state.fluorophore_df = edited_df
                st.success("✅ Changes saved successfully")
                st.rerun()

    # Add helpful resources section
    with st.expander("📚 Helpful Resources", expanded=False):
        tab1, tab2, tab3 = st.tabs(["FPbase Resources", "References", "Notes"])

        with tab1:
            st.markdown(
                """
            ### FPbase Resources
            - [FPbase Spectra Viewer](https://www.fpbase.org/spectra/)
            - [Activity Charts](https://www.fpbase.org/activity/)
            - [Popular Proteins](https://www.fpbase.org/proteins/)
            - [Spectra URL Builder](https://www.fpbase.org/spectra_url_builder/)
            """
            )

            # Embed spectra viewer using markdown
            st.markdown(
                """
                <iframe 
                    src="https://www.fpbase.org/spectra/?embed=true" 
                    width="100%" 
                    height="600" 
                    frameborder="0"
                    style="border:none;">
                </iframe>
                """,
                unsafe_allow_html=True,
            )

        with tab2:
            st.markdown(
                """
            ### Two-Photon Cross Section References
            Peak two-photon absorption cross sections compiled from:
            - 🔵 Dana et al. (2016) [26]
            - ⬛ Drobizhev et al. (2011) [27]
            - 💗 Harris [28]
            - 🔷 Kobat et al. (2009) [29]
            - ⬜ Xu et al. (1996) [30]
            """
            )

        with tab3:
            st.info(
                """
            **Note:** Organic dyes are not yet searchable in the database, but spectra 
            for a selection of organic dyes are available on the 
            [spectra page](https://www.fpbase.org/spectra/).
            
            You can manually add data from literature sources using the data editor above.
            """
            )
