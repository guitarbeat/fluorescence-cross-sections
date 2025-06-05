import requests
import streamlit as st
import logging # Added

logger = logging.getLogger(__name__) # Added

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzFM0_G7vy934oinoVqtFdCfErkYgU-dmxcxLw6mPMT9MBRlV4z-HbC5QB4KjcSZNoRRA/exec"

@st.cache_data(ttl=300) # Added caching for 5 minutes
def fetch_data(sheet_name):
    params = {
        'sheetName': sheet_name
    }
    try: # Added try/except block
        response = requests.get(WEB_APP_URL, params=params, timeout=15) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if isinstance(data, dict) and data.get('status') == 'error':
            logger.error(f"Google Apps Script Error for {sheet_name}: {data.get('message')}") # Log error
            st.error(f"Error fetching data for {sheet_name}: {data.get('message')}")
            return None
        return data
    except requests.exceptions.RequestException as e: # Catch request exceptions
        logger.error(f"Failed to fetch data for {sheet_name}: {e}")
        st.error(f'Failed to fetch data for {sheet_name}. Please check connection or try again later.')
        return None

def send_data(sheet_name, data):
    params = {
        'sheetName': sheet_name
    }
    headers = {'Content-Type': 'application/json'}
    try: # Added try/except block
        response = requests.post(WEB_APP_URL, params=params, json=data, headers=headers, timeout=20) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        if result.get('status') == 'success':
            st.success(result.get('message', 'Data sent successfully.'))
        else:
            logger.error(f"Google Apps Script Error sending data to {sheet_name}: {result.get('message')}") # Log error
            st.error(result.get('message', 'Unknown error sending data.'))
    except requests.exceptions.RequestException as e: # Catch request exceptions
        logger.error(f"Failed to send data to {sheet_name}: {e}")
        st.error(f'Failed to send data to {sheet_name}. Please check connection or try again later.')
