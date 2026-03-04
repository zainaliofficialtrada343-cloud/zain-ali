import database_helper as db
import streamlit as st
import pandas as pd
from datetime import datetime
from login_ui import show_login_page, local_css

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="BioCloud Lab Pro", layout="wide", page_icon="🧪")

# --- 2. SESSION STATE ---
if 'temp_tests' not in st.session_state:
    st.session_state.temp_tests = [] 
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def check_login(u, p):
    if u == "admin" and p == "lab786":
        st.session_state['auth'] = True
        st.rerun()
    else:
        st.error("Invalid Username or Password")

# --- 3. AUTH CHECK ---
if not st.session_state['auth']:
    show_login_page(check_login)
else:
    local_css("style.css")
    
    # Data Load
    df = db.get_full_data()
    today = str(datetime.now().date())
    required_cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]

    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🧪 BioCloud Pro</h1>", unsafe_allow_html=True)
        
        cash_df = df[df['Date'] == today] if not df.empty else pd.DataFrame()
        total_cash = pd.to_numeric(cash_df['Paid_Amount'], errors='coerce').sum() if not cash_df.empty else 0
        total_dues = pd.to_numeric(cash_df['Remaining'], errors='coerce').sum() if not cash_df.empty else 0
        
        st.metric("Aaj Ka Cash", f"Rs. {total_cash}")
        st.metric("Aaj Ke Dues", f"Rs. {total_dues}")
        
        st.divider()
        menu = st.radio("Navigation", ["Registration", "Dues & Reports", "Excel History"])
        if st.button("Logout"):
            st.session_state['auth'] = False
            st.rerun()

    if menu == "Registration":
        st.header("New Patient Registration")
        
        tdf = db.get_tests_list()
        test_options = sorted(tdf["Test_Name"].unique().tolist()) if not tdf.empty else []
        test_rate_dict = dict(zip(tdf["Test_Name"], tdf["Rate"])) if not tdf.empty else {}

        with st.expander("➕ Add New Test Type", expanded=False):
            c_n1, c_n2, c_n3 = st.columns([2, 1, 1])
            new_t_name = c_n1.text_input("New Test Name")
            new_t_rate = c_n2.number_input("Rate", 0)
            if c_n3.button("Save Test"):
                if new_t_name:
                    db.save_test_online(pd.DataFrame([{"Test_Name": new_t_name, "Rate": new_t_rate}]))
                    st.success("Test Added!")
                    st.rerun()

        with st.expander("Patient Info", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            p_name = c1.text_input("Patient Name")
            p_age = c2.number_input("Age", 1, 120, 25)
            p_gender = c3.selectbox("Gender", ["Male", "Female", "Other"])

        st.subheader("Add Tests")
        col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
        selected_t = col_t1.selectbox("Select Test", ["--- Select ---"] + test_options)
        default_rate = int(test_rate_dict.get(selected_t, 0)) if selected_t != "--- Select ---" else 0
        entered_rate = col_t2.number_input("Rate (Rs.)", value=default_rate, key="rate_in")

        if col_t3.button("➕ Add"):
            if selected_t != "--- Select ---":
                st.session_state.temp_tests.append({"Test": selected_t, "Rate": entered_rate})
                st.rerun()

        if st.session_state.temp_tests:
            total_bill = sum(t['Rate'] for t in st.session_state.temp_tests)
            for i, t in enumerate(st.session_state.temp_tests):
                st.write(f"{i+1}. {t['Test']} - Rs. {t['Rate']}")
            paid_amt = st.number_input("Paid Amount", 0)
            if st.button("💾 Final Save"):
                if p_name:
                    all_tests = ", ".join([t['Test'] for t in st.session_state.temp_tests])
                    rem = total_bill - paid_amt
                    new_id = len(df) + 1
                    new_row = [new_id, today, p_name, p_age, p_gender, all_tests, total_bill, paid_amt, rem, "-", "-", ("Paid" if rem<=0 else "Pending")]
                    db.save_record_online(pd.DataFrame([new_row], columns=required_cols))
                    st.session_state.temp_tests = [] 
                    st.success("Saved!")
                    st.rerun()

    elif menu == "Dues & Reports":
        st.header("Update Records")
        pending_df = df[(df["Remaining"] > 0) | (df["Result"] == "-")] if not df.empty else pd.DataFrame()
        if not pending_df.empty:
            sel_patient = st.selectbox("Select Patient", pending_df["Name"].tolist())
            p_data = df[df["Name"] == sel_patient].iloc[-1]
            st.warning(f"Dues: Rs. {p_data['Remaining']}")
            add_p = st.number_input("Add Payment", 0)
            res_v = st.text_input("Result", value=p_data['Result'])
            if st.button("Update"):
                new_paid = p_data["Paid_Amount"] + add_p
                new_rem = p_data["Total_Bill"] - new_paid
                df.loc[df["ID"] == p_data["ID"], ["Paid_Amount", "Remaining", "Status", "Result"]] = [new_paid, new_rem, ("Paid" if new_rem<=0 else "Pending"), res_v]
                db.conn.update(data=df, worksheet="Sheet1")
                st.success("Updated!")
                st.rerun()
        else:
            st.success("Sab clear hai!")

    elif menu == "Excel History":
        st.header("Database")
        st.dataframe(df, use_container_width=True, hide_index=True)