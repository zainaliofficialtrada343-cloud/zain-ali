import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Connection setup
conn = st.connection("gsheets", type=GSheetsConnection)

def get_full_data():
    try:
        return conn.read(worksheet="Sheet1", ttl=0).dropna(how="all")
    except:
        cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
        return pd.DataFrame(columns=cols)

def get_tests_list():
    try:
        return conn.read(worksheet="Sheet2", ttl=0).dropna(how="all")
    except:
        return pd.DataFrame(columns=["Test_Name", "Rate"])

def save_record_online(new_row_df):
    existing_data = get_full_data()
    # Yahan naam 'updated_data' hai
    updated_data = pd.concat([existing_data, new_row_df], ignore_index=True)
    # To neechay bhi 'updated_data' hi istemal kiya hai
    conn.update(data=updated_data, worksheet="Sheet1")
    st.cache_data.clear()

def save_test_online(new_test_df):
    existing_tests = get_tests_list()
    # Yahan naam 'updated_tests' hai
    updated_tests = pd.concat([existing_tests, new_test_df], ignore_index=True)
    # To neechay bhi 'updated_tests' hi istemal kiya hai
    conn.update(data=updated_tests, worksheet="Sheet2")
    st.cache_data.clear()