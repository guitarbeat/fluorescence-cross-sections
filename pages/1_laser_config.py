import streamlit as st

from src.components.laser_manager import render_laser_manager
from src.pages.common import render_footer
from src.state.session_state import initialize_session_state

initialize_session_state()

st.header("Laser Configuration", help="Configure and manage laser settings")

container = st.container(border=True)
with container:
    st.caption("Configure and manage laser settings for visualization")
    render_laser_manager()

render_footer()
