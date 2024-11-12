from dataclasses import dataclass
from typing import Tuple
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.api.google import fetch_data, send_data


@dataclass
class LaserConfig:
    """Configuration for default lasers"""

    name: str
    wavelength_range: Tuple[int, int]
    color: str


DEFAULT_LASERS = [
    LaserConfig("Ti:Sapphire", (800, 1000), "#ff4b4b"),  # Red
    LaserConfig("Yb fiber", (1050, 1070), "#4b4bff"),  # Blue
    LaserConfig("2C2P", (1150, 1200), "#37c463"),  # Green
    LaserConfig("Diamond", (1250, 1300), "#ff9d42"),  # Orange
    LaserConfig("Er fiber", (1550, 1600), "#42fff9"),  # Cyan
    LaserConfig("OPO/OPA", (1100, 2200), "#f942ff"),  # Magenta
]

# Add constant for laser data path
LASER_DATA_PATH = Path("data/lasers.csv")


def initialize_laser_data() -> pd.DataFrame:
    """Create a DataFrame from default laser configurations or load from CSV."""
    if LASER_DATA_PATH.exists():
        return pd.read_csv(LASER_DATA_PATH)
    
    # If no CSV exists, create from defaults
    default_df = pd.DataFrame(
        {
            "Name": [laser.name for laser in DEFAULT_LASERS],
            "Start_nm": [laser.wavelength_range[0] for laser in DEFAULT_LASERS],
            "End_nm": [laser.wavelength_range[1] for laser in DEFAULT_LASERS],
            "Color": [laser.color for laser in DEFAULT_LASERS],
        }
    )
    
    # Save default configuration
    LASER_DATA_PATH.parent.mkdir(exist_ok=True)
    default_df.to_csv(LASER_DATA_PATH, index=False)
    return default_df


def get_laser_df() -> pd.DataFrame:
    """Get laser DataFrame from Google Sheets or fallback to CSV."""
    if "laser_df" not in st.session_state:
        # Try to get data from Google Sheets first
        sheets_data = fetch_data("lasers")
        
        if sheets_data is not None:
            # Convert Google Sheets data to DataFrame
            st.session_state.laser_df = pd.DataFrame(sheets_data)
        else:
            # Fallback to CSV if Google Sheets fails
            st.session_state.laser_df = initialize_laser_data()
    
    return st.session_state.laser_df


def add_laser(name: str, start_nm: float, end_nm: float, color: str) -> bool:
    """Add a new laser to the session state and save to CSV."""
    if not name:
        return False

    try:
        new_laser = pd.DataFrame(
            {
                "Name": [name],
                "Start_nm": [start_nm],
                "End_nm": [end_nm],
                "Color": [color],
            }
        )

        laser_df = get_laser_df()
        st.session_state.laser_df = pd.concat([laser_df, new_laser], ignore_index=True)
        
        # Save to CSV
        save_laser_data(st.session_state.laser_df)
        return True

    except Exception as e:
        st.error(f"Error adding laser: {str(e)}")
        return False


def save_laser_data(df: pd.DataFrame) -> None:
    """Save laser data to both Google Sheets and CSV."""
    try:
        # Save to Google Sheets
        data = df.to_dict('records')
        send_data("lasers", data)
        
        # Backup to CSV
        LASER_DATA_PATH.parent.mkdir(exist_ok=True)
        df.to_csv(LASER_DATA_PATH, index=False)
    except Exception as e:
        st.error(f"Failed to save laser data: {str(e)}")


def render_add_laser_form() -> None:
    """Render the form for adding a new laser."""
    # Get global wavelength range
    wavelength_range = st.session_state.get("global_params", {}).get("wavelength_range", (700, 2400))
    min_wavelength, max_wavelength = wavelength_range
    
    with st.form("add_laser_form"):
        name = st.text_input("Name", key="new_laser_name")
        col1, col2 = st.columns(2)
        with col1:
            start_nm = st.number_input(
                "Start (nm)", 
                value=min_wavelength,  # Use global min
                min_value=min_wavelength,
                max_value=max_wavelength
            )
        with col2:
            end_nm = st.number_input(
                "End (nm)", 
                value=min(max_wavelength, start_nm + 200),  # Reasonable default span
                min_value=min_wavelength,
                max_value=max_wavelength
            )
        color = st.color_picker("Color", "#00ff00", key="new_laser_color")

        if st.form_submit_button("Add Laser", use_container_width=True):
            if add_laser(name, start_nm, end_nm, color):
                st.success(f"Added laser: {name}")
                st.rerun()
            else:
                st.error("Please provide a name for the laser")


def render_laser_editor() -> None:
    """Render the interface for editing existing lasers."""
    st.session_state.edited_df = st.data_editor(
        get_laser_df(),
        num_rows="dynamic",
        column_config={
            "Name": st.column_config.TextColumn(
                "Name",
                help="Laser name",
            ),
            "Start_nm": st.column_config.NumberColumn(
                "Start (nm)",
                help="Starting wavelength",
                format="%d",
            ),
            "End_nm": st.column_config.NumberColumn(
                "End (nm)",
                help="Ending wavelength",
                format="%d",
            ),
            "Color": st.column_config.TextColumn(
                "Color",
                help="Laser color in plots (hex code)",
            ),
        },
        hide_index=True,
        key="laser_editor",
        use_container_width=True,
    )

    # Keep only this save button
    if st.button("💾 Save Changes", use_container_width=True, key="laser_editor_save"):
        try:
            # Save to Google Sheets
            data = st.session_state.edited_df.to_dict('records')
            send_data("lasers", data)
            
            # Update session state after successful save
            st.session_state.laser_df = st.session_state.edited_df
            
            # Backup to CSV
            LASER_DATA_PATH.parent.mkdir(exist_ok=True)
            st.session_state.edited_df.to_csv(LASER_DATA_PATH, index=False)
            
            st.success("Changes saved successfully!")
        except Exception as e:
            st.error(f"Failed to save changes: {str(e)}")

    # Add download button
    if not st.session_state.edited_df.empty:
        csv = st.session_state.edited_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Laser Config",
            data=csv,
            file_name="laser_config.csv",
            mime="text/csv",
            key="laser_download"
        )


def render_color_picker() -> None:
    """Render the color picker interface."""
    with st.popover("Change Colors"):
        if not st.session_state.edited_df.empty:
            selected_indices = st.multiselect(
                "Select lasers",
                options=st.session_state.edited_df.index,
                format_func=lambda x: st.session_state.edited_df.loc[x, "Name"],
            )

            if selected_indices:
                new_color = st.color_picker(
                    "Pick new color",
                    st.session_state.edited_df.loc[selected_indices[0], "Color"],
                )
                if st.button("Update Color"):
                    st.session_state.edited_df.loc[selected_indices, "Color"] = (
                        new_color
                    )


def render_laser_manager() -> None:
    """Render the laser management interface."""
    with st.container():
        # Initialize show_lasers in session state if it doesn't exist
        if "show_lasers" not in st.session_state:
            st.session_state.show_lasers = False
            
        # Use only session state value, no default in toggle
        show_lasers = st.toggle(
            "Show Lasers",
            key="show_lasers",
            help="Toggle visibility of laser ranges on all plots",
        )
        
        if show_lasers:  # Use the toggle's return value
            # Remove tabs and just show editor directly
            render_laser_editor()
            render_color_picker()


def configure_plot_layout(fig: go.Figure, plot_type: str) -> None:
    """Configure the plot layout for laser overlays."""
    main_domain = [0, 0.85]

    # Configure axis domains
    if plot_type == "tissue":
        fig.update_layout(
            yaxis=dict(domain=main_domain), yaxis2=dict(domain=main_domain)
        )
    else:  # cross_section
        fig.update_layout(yaxis=dict(domain=main_domain))

    # Update layout with transparent background and hidden axes
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis3=dict(
            domain=[0.87, 0.92],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[0, 1],
            fixedrange=True,
            anchor="x",
            showline=False,
            visible=False,
            autorange=False,  # Disable autoranging
        ),
        yaxis4=dict(
            domain=[0.93, 1.0],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[0, 1],
            fixedrange=True,
            anchor="x",
            showline=False,
            visible=False,
            autorange=False,  # Disable autoranging
        ),
        xaxis=dict(
            showline=True,
            mirror=False,
            showgrid=False,
        ),
    )


def add_laser_overlays(fig: go.Figure) -> None:
    """Add laser overlays and annotations to the plot."""
    laser_df = get_laser_df()
    for _, laser in laser_df.iterrows():
        # Check if it's a single wavelength (start == end)
        is_single_wavelength = laser["Start_nm"] == laser["End_nm"]
        
        if is_single_wavelength:
            # Add star marker for single wavelength with smaller size
            fig.add_trace(
                go.Scatter(
                    x=[laser["Start_nm"]],
                    y=[0.5],
                    mode="markers",
                    marker=dict(
                        symbol="star",
                        size=15,  # Reduced from 20 to 15
                        color=laser["Color"],
                        line=dict(color=laser["Color"], width=2),
                    ),
                    showlegend=False,
                    yaxis="y3",
                )
            )
        else:
            # Add colored rectangle for wavelength range
            fig.add_shape(
                type="rect",
                x0=laser["Start_nm"],
                x1=laser["End_nm"],
                y0=0,
                y1=1,
                fillcolor=laser["Color"],
                opacity=0.3,
                layer="above",
                line_width=0,
                yref="y3",
            )

        # Add text above the marker/rectangle
        fig.add_annotation(
            x=(laser["Start_nm"] + laser["End_nm"]) / 2,
            y=0.5,
            text=laser["Name"],
            showarrow=False,
            yref="y4",
            font=dict(size=10, color=laser["Color"]),
        )


def overlay_lasers(fig: go.Figure, plot_type: str = "tissue") -> go.Figure:
    """Add laser overlays to a plot with consistent positioning."""
    if not st.session_state.get("show_lasers"):
        return fig

    # Add empty trace for laser axis
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            yaxis="y3",
            showlegend=False,
        )
    )

    configure_plot_layout(fig, plot_type)
    add_laser_overlays(fig)

    return fig
