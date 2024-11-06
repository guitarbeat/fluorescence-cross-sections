import streamlit as st
import plotly.graph_objects as go
from src.models.laser_model import initialize_laser_data, add_laser

DEFAULT_LASERS: dict[str, list] = {
    "Name": ["Ti:Sapphire", "Yb fiber", "2C2P", "Diamond", "Er fiber", "OPO/OPA"],
    "Range": [
        (800, 1000),
        (1050, 1070),
        (1150, 1200),
        (1250, 1300),
        (1550, 1600),
        (1100, 2200),
    ],
    "Color": [
        "#ff4b4b",  # Red
        "#4b4bff",  # Blue
        "#37c463",  # Green
        "#ff9d42",  # Orange
        "#42fff9",  # Cyan
        "#f942ff",  # Magenta
    ],
}


def render_laser_manager() -> None:
    """Render the laser management interface."""
    st.markdown("### Laser Management")

    # Initialize laser data if needed
    initialize_laser_data()

    # Global laser visibility toggle
    st.toggle(
        "Show Lasers",
        value=st.session_state.get("show_lasers", True),
        key="show_lasers",
        help="Toggle visibility of laser ranges on all plots",
    )

    if st.session_state.show_lasers:  # Only show laser controls if lasers are visible
        with st.expander("Laser Controls", expanded=False):  # Start collapsed
            # Add new laser form
            st.markdown("#### Add New Laser")
            with st.form("add_laser_form"):
                name = st.text_input("Name", key="new_laser_name")
                color = st.color_picker("Color", "#00ff00", key="new_laser_color")

                if st.form_submit_button("Add Laser", use_container_width=True):
                    if add_laser(name, 800, 1000, color):  # Default range
                        st.success(f"Added laser: {name}")
                        st.rerun()
                    else:
                        st.error("Please provide a name for the laser")

            # Existing lasers table as editable dataframe
            st.markdown("#### Existing Lasers")

            edited_df = st.data_editor(
                st.session_state.laser_df,
                num_rows="dynamic",
                column_config={
                    "Name": st.column_config.TextColumn(
                        "Name",
                        help="Laser name",
                        required=True,
                    ),
                    "Start_nm": st.column_config.NumberColumn(
                        "Start (nm)",
                        help="Starting wavelength",
                        min_value=700,
                        max_value=2400,
                        step=1,
                        format="%d",
                    ),
                    "End_nm": st.column_config.NumberColumn(
                        "End (nm)",
                        help="Ending wavelength",
                        min_value=700,
                        max_value=2400,
                        step=1,
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

            # Color picker for selected row
            if not edited_df.empty:
                selected_indices = st.multiselect(
                    "Select laser to change color",
                    options=edited_df.index,
                    format_func=lambda x: edited_df.loc[x, "Name"],
                )

                if selected_indices:
                    new_color = st.color_picker(
                        "Pick new color", edited_df.loc[selected_indices[0], "Color"]
                    )
                    if st.button("Update Color"):
                        edited_df.loc[selected_indices, "Color"] = new_color

            if st.button("💾 Save Changes", use_container_width=True):
                st.session_state.laser_df = edited_df
                st.success("Laser changes saved")
                st.rerun()


def overlay_lasers(fig: go.Figure, plot_type: str = "tissue") -> go.Figure:
    """Add laser overlays to a plot with consistent positioning.

    Args:
        fig: The plotly figure to add lasers to
        plot_type: Either "tissue" or "cross_section" to determine layout
    """
    if not st.session_state.get("show_lasers", True):
        return fig

    # Configure layout for laser domain
    if plot_type == "cross_section":
        main_domain = [0, 0.9]
        laser_domain = [0.92, 1.0]
    else:  # tissue plot
        main_domain = [0, 0.9]
        laser_domain = [0.92, 1.0]

    # Update layout to accommodate laser domain
    if plot_type == "tissue":
        fig.update_layout(
            yaxis=dict(domain=main_domain), yaxis2=dict(domain=main_domain)
        )
    else:
        fig.update_layout(yaxis=dict(domain=main_domain))

    # Create a new y-axis for lasers
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            yaxis="y3",
            showlegend=False,
        )
    )

    # Configure the laser axis
    fig.update_layout(
        yaxis3=dict(
            domain=laser_domain,
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[0, 1],
            fixedrange=True,
            anchor="x",
        )
    )

    # Add laser annotations
    if hasattr(st.session_state, "laser_df"):
        for _, laser in st.session_state.laser_df.iterrows():
            # Add shaded region for laser range
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

            # Add laser label
            fig.add_annotation(
                x=(laser["Start_nm"] + laser["End_nm"]) / 2,
                y=0.5,
                text=laser["Name"],
                showarrow=False,
                yref="y3",
                font=dict(size=10, color=laser["Color"]),
            )

    return fig
