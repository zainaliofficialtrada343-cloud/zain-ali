import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Connection setup
conn = st.connection("gsheets", type=GSheetsConnection)

def get_full_data():
    """Sheet1 se patients ka record parhna"""
    try:
        return conn.read(worksheet="Sheet1", ttl=0).dropna(how="all")
    except Exception as e:
        st.error(f"Sheet1 Error: {e}")
        cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
        return pd.DataFrame(columns=cols)

def get_tests_list():
    """Sheet2 se tests ki list parhna"""
    try:
        # Ye line aapke 203 tests Sheet2 se uthayegi
        return conn.read(worksheet="Sheet2", ttl=0).dropna(how="all")
    except Exception as e:
        st.error(f"Sheet2 Error: {e}")
        return pd.DataFrame(columns=["Test_Name", "Rate"])

def save_record_online(new_row_df):
    """Sheet1 mein naya record save karna"""
    try:
        existing_data = get_full_data()
        updated_data = pd.concat([existing_data, new_row_df], ignore_index=True)
        conn.update(data=updated_data, worksheet="Sheet1")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Save Record Error: {e}")

def save_test_online(new_test_df):
    """Sheet2 mein naya test save karna"""
    try:
        existing_tests = get_tests_list()
        updated_tests = pd.concat([existing_tests, new_test_df], ignore_index=True)
        conn.update(data=updated_tests, worksheet="Sheet2")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Save Test Error: {e}")