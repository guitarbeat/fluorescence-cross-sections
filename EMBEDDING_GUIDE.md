# Embedding Guide

## 🚀 How to Embed in Another Streamlit Project

The Deep Tissue Imaging Optimizer is now designed to be easily embedded as a page in other Streamlit projects.

### Method 1: Direct Function Import

```python
import streamlit as st
from tissue_imaging_page import render_tissue_imaging_page

# In your main app or page
def tissue_imaging_page():
    render_tissue_imaging_page()

# Add to your page navigation
pages = {
    "Home": home_page,
    "Tissue Imaging": tissue_imaging_page,  # Add this line
    "Other Page": other_page
}
```

### Method 2: Streamlit Pages (Recommended)

Create a file called `pages/tissue_imaging.py`:

```python
import streamlit as st
from tissue_imaging_page import render_tissue_imaging_page

st.set_page_config(
    page_title="Tissue Imaging",
    page_icon="🔬",
    layout="wide"
)

render_tissue_imaging_page()
```

### Method 3: Tab Integration

```python
import streamlit as st
from tissue_imaging_page import render_tissue_imaging_page

# In your main app
tab1, tab2, tab3 = st.tabs(["Overview", "Tissue Imaging", "Results"])

with tab1:
    st.write("Your overview content")

with tab2:
    render_tissue_imaging_page()  # Embed here

with tab3:
    st.write("Your results content")
```

## 📁 Required Files

Make sure to copy these files to your project:

```
your_project/
├── tissue_imaging_page.py          # Main page function
├── src/
│   ├── config.py                   # Configuration
│   ├── core.py                     # Core functionality
│   ├── components/
│   │   ├── dashboard_utils.py      # Dashboard utilities
│   │   ├── common.py               # Common components
│   │   ├── tissue_config.py        # Mathematical model
│   │   ├── laser_manager.py        # Laser management
│   │   ├── fluorophore_viewer.py   # Fluorophore viewer
│   │   └── ui_components.py        # UI components
│   ├── plots/
│   │   ├── cross_section_plot.py   # Cross-section plotting
│   │   ├── tissue_view.py          # Tissue penetration plots
│   │   └── zipfel_cross_sections.py # Additional plots
│   ├── api/
│   │   ├── fpbase_client.py        # FPbase API client
│   │   ├── fpbase_types.py         # API types
│   │   └── search_form.py          # Search functionality
│   ├── utils/
│   │   └── data_loader.py          # Data loading utilities
│   └── data/                       # Data files
└── data/                           # Data directory
```

## 🎨 Features

The embedded page includes:

- ✅ **Compact Design**: No sidebar, condensed layout
- ✅ **Metric Cards**: Real-time parameter display
- ✅ **Parameter Controls**: 4-column compact layout
- ✅ **Analysis Plots**: Side-by-side visualization
- ✅ **Collapsible Sections**: Laser config and fluorophore library (expanders), math model (checkbox toggle)
- ✅ **Professional Styling**: Custom CSS included
- ✅ **Error Handling**: Graceful error management
- ✅ **Responsive**: Works well in different layouts

## 🔧 Customization

### Modify the Header
Edit the header in `tissue_imaging_page.py`:

```python
st.markdown("""
<div style='text-align: center; padding: 0.5rem 0; margin-bottom: 1rem;'>
    <h2 style='color: #0f4c81; margin: 0; font-size: 2rem;'>
        Your Custom Title Here
    </h2>
</div>
""", unsafe_allow_html=True)
```

### Hide Sections
Comment out sections you don't need:

```python
# Laser Configuration (expander)
# with st.expander("🔬 Laser Configuration", expanded=False):
#     # Laser config code...

# Mathematical Model (checkbox toggle)
# show_math_model = st.checkbox("🧮 Show Mathematical Model", value=False)
# if show_math_model:
#     # Math model code...

# Fluorophore Library (expander)
# with st.expander("🔬 Fluorophore Library", expanded=False):
#     # Library code...
```

### Custom Styling
Modify `dashboard_utils.py` to change colors, spacing, etc.

## 📊 Data Requirements

The page expects these data files in the `data/` directory:
- `fluorophores.csv` - Fluorophore data
- `lasers.csv` - Laser configuration
- `2p-xsections/` - Cross-section data files

## 🚀 Performance

The page is optimized for embedding:
- Minimal dependencies
- Efficient caching
- Compact layout
- Fast loading

## 💡 Tips

1. **Layout**: Use `layout="wide"` in your page config for best results
2. **Caching**: The page uses Streamlit caching for performance
3. **State**: Session state is managed internally
4. **Errors**: All errors are handled gracefully with user-friendly messages