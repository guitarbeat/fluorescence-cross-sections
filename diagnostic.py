"""Diagnostic script to test app components."""
import streamlit as st
import sys
import traceback

def test_imports():
    """Test all imports."""
    st.header("Testing Imports")
    
    try:
        from src.state.session_state import initialize_session_state
        st.success("✅ Session state imports successfully")
    except Exception as e:
        st.error(f"❌ Session state import failed: {e}")
        st.code(traceback.format_exc())
        return False
    
    try:
        from src.components.laser_manager import render_laser_manager
        st.success("✅ Laser manager imports successfully")
    except Exception as e:
        st.error(f"❌ Laser manager import failed: {e}")
        st.code(traceback.format_exc())
        return False
    
    try:
        from src.components.fluorophore_viewer import render_fluorophore_viewer
        st.success("✅ Fluorophore viewer imports successfully")
    except Exception as e:
        st.error(f"❌ Fluorophore viewer import failed: {e}")
        st.code(traceback.format_exc())
        return False
    
    return True

def test_session_state():
    """Test session state initialization."""
    st.header("Testing Session State")
    
    try:
        from src.state.session_state import initialize_session_state
        initialize_session_state()
        st.success("✅ Session state initialized successfully")
        
        # Check key data
        if "fluorophore_df" in st.session_state:
            st.success(f"✅ Fluorophore data loaded: {len(st.session_state.fluorophore_df)} rows")
        else:
            st.error("❌ Fluorophore data not loaded")
            
        if "laser_df" in st.session_state:
            st.success(f"✅ Laser data loaded: {len(st.session_state.laser_df)} rows")
        else:
            st.error("❌ Laser data not loaded")
            
        if "cross_sections" in st.session_state:
            st.success(f"✅ Cross-sections loaded: {len(st.session_state.cross_sections)} files")
        else:
            st.error("❌ Cross-sections not loaded")
            
    except Exception as e:
        st.error(f"❌ Session state initialization failed: {e}")
        st.code(traceback.format_exc())
        return False
    
    return True

def test_navigation():
    """Test navigation features."""
    st.header("Testing Navigation")
    
    try:
        # Test if navigation features are available
        st.write(f"st.navigation available: {hasattr(st, 'navigation')}")
        st.write(f"st.Page available: {hasattr(st, 'Page')}")
        
        if hasattr(st, 'Page'):
            # Test creating a page
            test_page = st.Page("test.py", title="Test", icon="🔬")
            st.success("✅ Page creation works")
        else:
            st.error("❌ st.Page not available")
            
    except Exception as e:
        st.error(f"❌ Navigation test failed: {e}")
        st.code(traceback.format_exc())
        return False
    
    return True

def main():
    st.set_page_config(
        page_title="Diagnostic",
        page_icon="🔬",
        layout="wide",
    )
    
    st.title("App Diagnostic")
    st.write("Testing app components step by step...")
    
    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Session State", test_session_state),
        ("Navigation", test_navigation),
    ]
    
    results = []
    for test_name, test_func in tests:
        with st.expander(f"Test: {test_name}", expanded=True):
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                st.error(f"Test {test_name} failed with exception: {e}")
                st.code(traceback.format_exc())
                results.append((test_name, False))
    
    # Summary
    st.header("Test Summary")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        st.write(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        st.success("🎉 All tests passed! The app should work correctly.")
    else:
        st.error("⚠️ Some tests failed. Check the details above.")

if __name__ == "__main__":
    main() 