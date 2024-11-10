import requests
import streamlit as st


WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzFM0_G7vy934oinoVqtFdCfErkYgU-dmxcxLw6mPMT9MBRlV4z-HbC5QB4KjcSZNoRRA/exec"



def fetch_data(sheet_name):
    params = {
        'sheetName': sheet_name
    }
    response = requests.get(WEB_APP_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and data.get('status') == 'error':
            st.error(data.get('message'))
            return None
        return data
    else:
        st.error('Failed to fetch data')
        return None

def send_data(sheet_name, data):
    params = {
        'sheetName': sheet_name
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(WEB_APP_URL, params=params, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            st.success(result.get('message'))
        else:
            st.error(result.get('message'))
    else:
        st.error('Failed to send data')