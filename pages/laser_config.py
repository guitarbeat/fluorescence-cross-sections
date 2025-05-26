"""Laser Configuration Page"""
import streamlit as st
from src.components.laser_manager import render_laser_manager

st.header("🎯 Laser Configuration")
st.caption("Configure and manage laser settings for visualization")

# Direct container with border for better visual separation
laser_container = st.container(border=True)
with laser_container:
    render_laser_manager()
