import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Google Sheets se connection banana
conn = st.connection("gsheets", type=GSheetsConnection)

def get_full_data():
    """Sheet1 se patients ka sara record uthana"""
    #
    try:
        df = conn.read(worksheet="Sheet1")
        return df.dropna(how="all") # Khali rows khatam karne ke liye
    except:
        # Agar sheet khali ho toh required columns ke saath khali DataFrame dena
        cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
        return pd.DataFrame(columns=cols)

def get_tests_list():
    """Sheet2 se tests aur unke rates uthana"""
    try:
        tdf = conn.read(worksheet="Sheet2")
        return tdf.dropna(how="all")
    except:
        return pd.DataFrame(columns=["Test_Name", "Rate"])

def save_record_online(new_row_df):
    """Naya record Google Sheet mein save karna"""
    #
    existing_df = get_full_data()
    # Naye record ko purane data ke niche jodna
    updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
    # Sheet1 mein wapis update kar dena
    conn.update(worksheet="Sheet1", data=updated_df)