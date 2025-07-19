"""UI components for the Deep Tissue Imaging Optimizer."""
from typing import Any, List, Tuple, Optional, Dict

import streamlit as st


def render_section_header(title: str, description: Optional[str] = None) -> None:
    """Render a consistent section header with optional description."""
    st.subheader(title)
    if description:
        st.write(description)


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

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme="streamlit",
        config={"displayModeBar": True, "responsive": True},
    )

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


def render_tabs_with_content(
    tab_configs: List[Tuple[str, callable, Optional[str]]]
) -> None:
    """
    Render tabs with content using consistent error handling.

    Args:
        tab_configs: List of (tab_name, content_function, info_message) tuples
    """
    tab_names = [config[0] for config in tab_configs]
    tabs = st.tabs(tab_names)

    for i, (tab_name, content_function, info_message) in enumerate(tab_configs):
        with tabs[i]:
            if info_message:
                st.info(info_message)
            render_error_boundary(
                content_function,
                f"Error loading {tab_name.lower()}"
            )


def render_expandable_section(
    title: str,
    content_function: callable,
    expanded: bool = False,
    error_message: Optional[str] = None,
    fallback_message: Optional[str] = None
) -> None:
    """
    Render an expandable section with consistent error handling.

    Args:
        title: Title for the expandable section
        content_function: Function to render the content
        expanded: Whether the section should be expanded by default
        error_message: Custom error message
        fallback_message: Optional fallback message to show after error
    """
    with st.expander(title, expanded=expanded):
        error_msg = error_message or f"Error loading {title.lower()}"
        render_error_boundary(content_function, error_msg, fallback_message)
