import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Connection setup
conn = st.connection("gsheets", type=GSheetsConnection)

def get_full_data():
    try:
        # TTL=0 zaroori hai taake har baar naya data aaye
        return conn.read(worksheet="Sheet1", ttl=0).dropna(how="all")
    except Exception as e:
        st.error(f"Sheet1 Error: {e}")
        cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
        return pd.DataFrame(columns=cols)

def get_tests_list():
    try:
        # Hum direct Sheet2 dhoond rahe hain
        df = conn.read(worksheet="Sheet2", ttl=0).dropna(how="all")
        if df.empty:
            return pd.DataFrame([{"Test_Name": "No Tests Found", "Rate": 0}])
        return df
    except Exception as e:
        # Agar Sheet2 na mile toh ye default dikhaye ga
        return pd.DataFrame([{"Test_Name": "CBC", "Rate": 500}, {"Test_Name": "Sugar", "Rate": 200}])

def save_record_online(new_row_df):
    existing_data = get_full_data()
    updated_data = pd.concat([existing_data, new_row_df], ignore_index=True)
    conn.update(data=updated_data, worksheet="Sheet1")
    st.cache_data.clear()

def save_test_online(new_test_df):
    existing_tests = get_tests_list()
    updated_tests = pd.concat([existing_tests, new_test_df], ignore_index=True)
    conn.update(data=updated_tests, worksheet="Sheet2")
    st.cache_data.clear()