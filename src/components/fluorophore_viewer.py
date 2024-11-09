import streamlit as st
from typing import Dict, Tuple
import pandas as pd
import numpy as np
import requests
from ..plots.zipfel_cross_sections import plot_cross_section

def get_reference_image_url(fluorophore_name: str) -> str:
    """
    Get the reference image URL for a given fluorophore.
    Handles common spelling variations.
    """
    base_url = "http://www.drbio.cornell.edu/images/CrossSectionJPGs"
    
    # Dictionary of filename corrections
    filename_corrections = {
        "Fluoresecein": "Fluorescein",
        # Add more corrections here if needed
    }
    
    # Use corrected filename if it exists, otherwise use original
    corrected_name = filename_corrections.get(fluorophore_name, fluorophore_name)
    
    return f"{base_url}/{corrected_name}.jpg"

def calculate_fluorophore_stats(df: pd.DataFrame, fluorophore_name: str) -> Dict[str, float]:
    """Calculate statistics for the fluorophore data."""
    stats = {}
    
    if fluorophore_name == "IntrinsicFluorophores":
        # Calculate stats for each fluorophore
        for col in ["riboflavin", "folic_acid", "cholecalciferol", "retinol"]:
            peak_idx = df[col].idxmax()
            stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
            stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
            stats[f"{col}_mean_cross_section"] = df[col].mean()
            
    elif fluorophore_name == "NADH-ProteinBound":
        # Calculate stats for each form
        for col in ["gm_mean", "gm_mdh", "gm_ad"]:
            peak_idx = df[col].idxmax()
            stats[f"{col}_peak_wavelength"] = df.loc[peak_idx, "wavelength"]
            stats[f"{col}_peak_cross_section"] = df.loc[peak_idx, col]
            stats[f"{col}_mean_cross_section"] = df[col].mean()
        if "sd" in df.columns:
            stats["mean_std_dev"] = df["sd"].mean()
            
    else:
        # Standard statistics for single-trace fluorophores
        cross_section_col = "cross_section" if "cross_section" in df.columns else df.columns[1]
        peak_idx = df[cross_section_col].idxmax()
        stats["peak_wavelength"] = df.loc[peak_idx, "wavelength"]
        stats["peak_cross_section"] = df.loc[peak_idx, cross_section_col]
        stats["mean_cross_section"] = df[cross_section_col].mean()
        if "std_dev" in df.columns:
            stats["mean_std_dev"] = df["std_dev"].mean()
    
    return stats

def format_stats(stats: Dict[str, float]) -> str:
    """Format statistics for display."""
    formatted = []
    for key, value in stats.items():
        if "wavelength" in key:
            formatted.append(f"**{key.replace('_', ' ').title()}:** {value:.0f} nm")
        elif "cross_section" in key:
            formatted.append(f"**{key.replace('_', ' ').title()}:** {value:.2e} GM")
        elif "std_dev" in key:
            formatted.append(f"**{key.replace('_', ' ').title()}:** {value:.2e}")
    return "\n\n".join(formatted)

def render_fluorophore_viewer(cross_sections: Dict[str, pd.DataFrame], key_prefix: str = "") -> None:
    """Render the fluorophore viewer component."""
    if not cross_sections:
        st.warning("No cross-section data available.")
        return

    # Create a dropdown for fluorophore selection
    fluorophore_names = sorted(cross_sections.keys())
    selected_fluorophore = st.selectbox(
        "Select Fluorophore",
        options=fluorophore_names,
        help="Choose a fluorophore to view its two-photon cross section data",
        key=f"{key_prefix}_fluorophore_selector"
    )

    # Create columns for plot and reference/stats
    col1, col2 = st.columns([2, 1])

    with col1:
        try:
            fig = plot_cross_section(
                cross_sections=cross_sections,
                selected_fluorophore=selected_fluorophore,
                height=500,
                width=700,
                show_error_bars=True
            )
            st.plotly_chart(fig, use_container_width=True, key=f"{key_prefix}_plot")
        except Exception as e:
            st.error(f"Error plotting data for {selected_fluorophore}: {str(e)}")

    with col2:
        # Statistics Section
        st.markdown("### Statistics")
        df = cross_sections[selected_fluorophore]
        stats = calculate_fluorophore_stats(df, selected_fluorophore)
        st.markdown(format_stats(stats))
        
        # Reference Image
        st.markdown("### Reference Plot")
        try:
            image_url = get_reference_image_url(selected_fluorophore)
            response = requests.get(image_url)
            if response.status_code == 200:
                st.image(
                    response.content,
                    caption=f"Reference plot for {selected_fluorophore}",
                    use_column_width=True
                )
            else:
                st.info(f"No reference image available at:\n{image_url}")
        except Exception as e:
            st.info(f"Could not load reference image from:\n{image_url}")

    # Data Table Section
    col1, col2 = st.columns([3, 1])
    with col1:
        show_data = st.checkbox(
            "Show Data Table", 
            key=f"{key_prefix}_show_data_{selected_fluorophore}"
        )
    with col2:
        # Add button to import to main table
        if st.button("📥 Add to Main Table", key=f"{key_prefix}_add_{selected_fluorophore}"):
            df = cross_sections[selected_fluorophore]
            
            # Determine which column contains the cross-section data
            # It could be 'GM', 'cross_section', or the second column
            if 'GM' in df.columns:
                cs_column = 'GM'
            elif 'cross_section' in df.columns:
                cs_column = 'cross_section'
            else:
                cs_column = df.columns[1]  # Assume second column is cross-section data
            
            # Find peak wavelength and cross section
            peak_idx = df[cs_column].idxmax()
            wavelength = df.index[peak_idx] if df.index.name == 'wavelength' else df.iloc[peak_idx].get('wavelength', df.iloc[peak_idx].name)
            
            peak_data = {
                "Name": selected_fluorophore,
                "Wavelength": float(wavelength),  # Ensure wavelength is a float
                "Cross_Section": float(df.iloc[peak_idx][cs_column]),  # Ensure cross-section is a float
                "Reference": "Zipfel Lab",  # Simplified reference
                "Em_Max": None,  # Add any additional columns that match your schema
                "QY": None,
                "EC": None,
                "pKa": None
            }
            
            # Add to fluorophore_df if it doesn't exist
            if "fluorophore_df" in st.session_state:
                new_df = pd.DataFrame([peak_data])
                st.session_state.fluorophore_df = pd.concat(
                    [st.session_state.fluorophore_df, new_df],
                    ignore_index=True
                ).drop_duplicates(subset=["Name"], keep="last")
                st.success(f"Added {selected_fluorophore} to main table!")
                st.rerun()
            else:
                st.error("Main fluorophore table not initialized")
    
    if show_data:
        df = cross_sections[selected_fluorophore]
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            key=f"{key_prefix}_dataframe"
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Data",
            data=csv,
            file_name=f"{selected_fluorophore}_cross_section.csv",
            mime="text/csv",
            key=f"{key_prefix}_download"
        )