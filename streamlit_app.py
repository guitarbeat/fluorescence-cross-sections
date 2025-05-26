"""
Modern Deep Tissue Imaging Optimizer using st.navigation
Clean, simple navigation without user modes.
"""
import logging
import streamlit as st
from src.state.session_state import initialize_session_state

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main application with clean navigation."""
    # Page configuration
    st.set_page_config(
        page_title="Deep Tissue Imaging Optimizer",
        layout="wide",
        initial_sidebar_state="collapsed",
        page_icon="🔬"
    )

    # Initialize session state
    initialize_session_state()

    # Add logo and branding
    st.logo("src/assets/favicon.png")

    # Define all pages
    laser_page = st.Page(
        "pages/laser_config.py",
        title="Laser Configuration",
        icon="🎯"
    )

    wavelength_page = st.Page(
        "pages/wavelength_settings.py",
        title="Wavelength Settings",
        icon="📊"
    )

    tissue_page = st.Page(
        "pages/tissue_parameters.py",
        title="Tissue Parameters",
        icon="🔬"
    )

    cross_sections_page = st.Page(
        "pages/cross_sections.py",
        title="Cross-sections",
        icon="📈",
        default=True  # Default landing page
    )

    tissue_analysis_page = st.Page(
        "pages/tissue_analysis.py",
        title="Tissue Analysis",
        icon="🧬"
    )

    library_page = st.Page(
        "pages/fluorophore_library.py",
        title="Fluorophore Library",
        icon="📚"
    )

    # Compact, high-density sidebar
    with st.sidebar:
        # Enhanced CSS for maximum information density
        st.markdown("""
        <style>
        .compact-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.6rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 0.6rem;
            font-weight: 600;
            font-size: 0.95em;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.4rem;
            margin: 0.4rem 0;
        }
        .status-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 0.4rem;
            text-align: center;
            font-size: 0.8em;
            line-height: 1.2;
        }
        .status-item.active {
            background: #d4edda;
            border-color: #c3e6cb;
            color: #155724;
        }
        .status-item.inactive {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.3rem;
            margin: 0.4rem 0;
        }
        .metric-compact {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 0.3rem;
            text-align: center;
            font-size: 0.75em;
            line-height: 1.2;
        }
        .metric-compact .label {
            color: #6c757d;
            font-size: 0.7em;
            margin-bottom: 0.1rem;
        }
        .metric-compact .value {
            font-weight: bold;
            color: #495057;
            font-size: 0.85em;
        }
        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 0.25rem;
            margin: 0.4rem 0;
        }
        .section-title {
            font-size: 0.85em;
            font-weight: 600;
            color: #495057;
            margin: 0.6rem 0 0.3rem 0;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 0.15rem;
        }
        .help-compact {
            font-size: 0.75em;
            line-height: 1.3;
        }
        .quick-adjust {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 0.4rem;
            margin: 0.3rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

        # Compact app header
        st.markdown(
            '<div class="compact-header">🔬 Deep Tissue Optimizer</div>', unsafe_allow_html=True)

        # Compact data status with grid layout
        st.markdown('<div class="section-title">📊 Status</div>',
                    unsafe_allow_html=True)

        fluoro_count = len(st.session_state.get("fluorophore_df", []))
        laser_count = len(st.session_state.get("laser_df", []))

        fluoro_status = "active" if fluoro_count > 0 else "inactive"
        laser_status = "active" if laser_count > 0 else "inactive"

        st.markdown(f"""
        <div class="status-grid">
            <div class="status-item {fluoro_status}">
                <div>🧬 Fluoro</div>
                <div><strong>{fluoro_count}</strong></div>
            </div>
            <div class="status-item {laser_status}">
                <div>🎯 Laser</div>
                <div><strong>{laser_count}</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Compact parameters in 2x2 grid
        st.markdown('<div class="section-title">⚙️ Parameters</div>',
                    unsafe_allow_html=True)

        if st.session_state.global_params and st.session_state.tissue_params:
            wl_range = st.session_state.global_params.get(
                "wavelength_range", (700, 1700))
            norm_wl = st.session_state.global_params.get(
                "normalization_wavelength", 1300)
            depth = st.session_state.tissue_params.get("depth", 1.0)
            water_content = st.session_state.tissue_params.get(
                "water_content", 0.75)

            st.markdown(f"""
            <div class="metric-grid">
                <div class="metric-compact">
                    <div class="label">Range</div>
                    <div class="value">{wl_range[0]}-{wl_range[1]}</div>
                </div>
                <div class="metric-compact">
                    <div class="label">Norm λ</div>
                    <div class="value">{norm_wl}</div>
                </div>
                <div class="metric-compact">
                    <div class="label">Depth</div>
                    <div class="value">{depth}mm</div>
                </div>
                <div class="metric-compact">
                    <div class="label">H₂O</div>
                    <div class="value">{water_content:.0%}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Compact actions in 3-column grid
        st.markdown('<div class="section-title">🚀 Actions</div>',
                    unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄", help="Reset all", use_container_width=True, key="reset_compact"):
                for key in ["fluorophore_df", "laser_df"]:
                    if key in st.session_state:
                        del st.session_state[key]
                initialize_session_state()
                st.rerun()

        with col2:
            # Quick parameter adjustment toggle
            if st.button("⚡", help="Quick adjust", use_container_width=True, key="quick_adjust"):
                st.session_state.show_quick_adjust = not st.session_state.get(
                    "show_quick_adjust", False)

        with col3:
            # Export config
            if st.button("💾", help="Export", use_container_width=True, key="export_compact"):
                export_data = {
                    "global_params": st.session_state.global_params,
                    "tissue_params": st.session_state.tissue_params
                }
                st.download_button(
                    "📥",
                    data=str(export_data),
                    file_name="config.json",
                    mime="application/json",
                    use_container_width=True,
                    key="download_compact"
                )

        # Quick parameter adjustment panel (collapsible)
        if st.session_state.get("show_quick_adjust", False):
            st.markdown(
                '<div class="section-title">⚡ Quick Adjust</div>', unsafe_allow_html=True)

            # Most commonly adjusted parameters in compact form
            new_norm = st.slider("Norm λ", 800, 2000,
                                 st.session_state.global_params.get(
                                     "normalization_wavelength", 1300),
                                 step=50, key="quick_norm", label_visibility="collapsed")
            st.session_state.global_params["normalization_wavelength"] = new_norm

            new_depth = st.slider("Depth (mm)", 0.1, 2.0,
                                  st.session_state.tissue_params.get(
                                      "depth", 1.0),
                                  step=0.1, key="quick_depth", label_visibility="collapsed")
            st.session_state.tissue_params["depth"] = new_depth

        # Ultra-compact help section
        st.markdown('<div class="section-title">❓ Help</div>',
                    unsafe_allow_html=True)

        with st.expander("Guide", expanded=False):
            st.markdown("""
            <div class="help-compact">
            <strong>Workflow:</strong> Config → Analysis → Library<br>
            <strong>⚡ Button:</strong> Quick parameter changes<br>
            <strong>Auto-save:</strong> All changes persist<br>
            <strong>🔄 Reset:</strong> Clear all data
            </div>
            """, unsafe_allow_html=True)

        # Minimal footer
        st.markdown("---")
        st.markdown('<div style="text-align: center; color: #6c757d; font-size: 0.65em;">v2.0 • <a href="https://www.fpbase.org" target="_blank">FPbase</a></div>', unsafe_allow_html=True)

    # Create simple navigation structure
    page_dict = {
        "Configuration": [laser_page, wavelength_page, tissue_page],
        "Analysis": [cross_sections_page, tissue_analysis_page],
        "Library": [library_page]
    }

    # Create navigation
    pg = st.navigation(page_dict)

    # Compact header with key metrics
    st.markdown("""
    <style>
    .header-metrics {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 1rem;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
    }
    .metric-item {
        text-align: center;
        padding: 0.5rem;
        background: white;
        border-radius: 6px;
        border: 1px solid #e9ecef;
    }
    .metric-item .label {
        font-size: 0.8em;
        color: #6c757d;
        margin-bottom: 0.25rem;
    }
    .metric-item .value {
        font-size: 1.1em;
        font-weight: bold;
        color: #495057;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.global_params and st.session_state.tissue_params:
        wl_range = st.session_state.global_params.get(
            "wavelength_range", (700, 1700))
        norm_wl = st.session_state.global_params.get(
            "normalization_wavelength", 1300)
        depth = st.session_state.tissue_params.get("depth", 1.0)
        water_content = st.session_state.tissue_params.get(
            "water_content", 0.75)
        absorption_threshold = st.session_state.global_params.get(
            "absorption_threshold", 50)

        st.markdown(f"""
        <div class="header-metrics">
            <div class="metric-item">
                <div class="label">Wavelength Range</div>
                <div class="value">{wl_range[0]}-{wl_range[1]} nm</div>
            </div>
            <div class="metric-item">
                <div class="label">Normalization λ</div>
                <div class="value">{norm_wl} nm</div>
            </div>
            <div class="metric-item">
                <div class="label">Tissue Depth</div>
                <div class="value">{depth} mm</div>
            </div>
            <div class="metric-item">
                <div class="label">Water Content</div>
                <div class="value">{water_content:.0%}</div>
            </div>
            <div class="metric-item">
                <div class="label">Absorption Threshold</div>
                <div class="value">{absorption_threshold}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Run the selected page
    pg.run()

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em; padding: 20px 0;'>
            Developed by Aaron Woods • Data from <a href="https://www.fpbase.org">FPbase</a>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
