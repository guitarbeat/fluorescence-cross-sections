"""UI components for the Deep Tissue Imaging Optimizer."""
from typing import Any, List, Tuple, Optional, Dict

import streamlit as st
from src.components.plot_utils import render_simple_plotly_chart


# Removed unused function render_parameter_control


def render_plot_with_settings(
    fig,
    title: Optional[str] = None,
    settings_component: Optional[callable] = None,
    settings_title: str = "⚙️ Settings",
    settings_help: str = "Customize plot settings"
) -> None:
    """
    Render a plot with optional settings popover.

    Args:
        fig: Plotly figure to display
        title: Optional title for the plot section
        settings_component: Optional function to render settings
        settings_title: Title for the settings popover
        settings_help: Help text for the settings popover
    """
    if title:
        st.markdown(f"### {title}")

    render_simple_plotly_chart(fig)

    if settings_component:
        with st.popover(settings_title, help=settings_help):
            settings_component()


def render_data_editor(
    df,
    column_config: Dict[str, Any],
    column_order: List[str],
    key: str,
    title: Optional[str] = None
) -> Any:
    """
    Render a data editor with consistent configuration.

    Args:
        df: DataFrame to edit
        column_config: Column configuration dictionary
        column_order: List of column names in display order
        key: Unique key for the editor
        title: Optional title for the section

    Returns:
        The edited DataFrame
    """
    if title:
        st.markdown(f"### {title}")

    return st.data_editor(
        df,
        num_rows="dynamic",
        column_config=column_config,
        column_order=column_order,
        use_container_width=True,
        hide_index=True,
        key=key,
    )


def render_save_button(
    save_function: callable,
    success_message: str = "Changes saved!",
    button_text: str = "Save Changes",
    button_type: str = "primary",
    key: str = "save_button"
) -> None:
    """
    Render a save button with consistent error handling.

    Args:
        save_function: Function to call when saving
        success_message: Message to show on successful save
        button_text: Text for the button
        button_type: Button type ('primary', 'secondary')
        key: Unique key for the button
    """
    if st.button(button_text, type=button_type, key=key):
        try:
            save_function()
            st.success(success_message)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to save changes: {str(e)}")


def render_error_boundary(
    component_function: callable,
    error_message: str,
    fallback_message: Optional[str] = None
) -> None:
    """
    Render a component with consistent error handling.

    Args:
        component_function: Function to render the component
        error_message: Message to show if component fails
        fallback_message: Optional fallback message
    """
    try:
        component_function()
    except Exception as e:
        st.error(f"{error_message}: {e}")
        if fallback_message:
            st.info(fallback_message)
