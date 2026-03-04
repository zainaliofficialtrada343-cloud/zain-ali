import streamlit as st
import pandas as pd
import os
from datetime import datetime
from login_ui import show_login_page, local_css

# --- 1. CSV DATABASE CONFIG ---
PATIENT_FILE = "data_db.csv"
TESTS_FILE = "tests_db.csv"

def get_full_data():
    if os.path.exists(PATIENT_FILE):
        return pd.read_csv(PATIENT_FILE)
    else:
        cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
        return pd.DataFrame(columns=cols)

def get_tests_list():
    if os.path.exists(TESTS_FILE):
        return pd.read_csv(TESTS_FILE)
    else:
        return pd.DataFrame([{"Test_Name": "CBC", "Rate": 500}, {"Test_Name": "Sugar", "Rate": 200}])

def save_record_local(new_row_df):
    existing_data = get_full_data()
    updated_data = pd.concat([existing_data, new_row_df], ignore_index=True)
    updated_data.to_csv(PATIENT_FILE, index=False)

def save_test_local(new_test_df):
    existing_tests = get_tests_list()
    updated_tests = pd.concat([existing_tests, new_test_df], ignore_index=True)
    updated_tests.to_csv(TESTS_FILE, index=False)

# --- NEW: SLIP DESIGN FUNCTION ---
def show_receipt(data):
    # data can be a list or a pandas series
    val = data.tolist() if hasattr(data, 'tolist') else data
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border: 2px dashed #333; width: 300px; color: black; font-family: 'Courier New', monospace; margin: auto;">
            <div style="text-align: center; font-weight: bold; font-size: 20px;">🧪 BIOCLOUD LAB</div>
            <div style="text-align: center; font-size: 10px;">Modern Diagnostic Center</div>
            <hr style="border-top: 1px solid black;">
            <div style="font-size: 12px;">
                <b>ID:</b> {val[0]} <br>
                <b>Date:</b> {val[1]} <br>
                <b>Name:</b> {val[2]} <br>
                <b>Age/Sex:</b> {val[3]} / {val[4]}
            </div>
            <hr style="border-top: 1px solid black;">
            <div style="font-size: 12px; font-weight: bold;">Tests:</div>
            <div style="font-size: 11px;">{val[5]}</div>
            <hr style="border-top: 1px solid black;">
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>Total:</span> <span>Rs. {val[6]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Paid:</span> <span>Rs. {val[7]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: red;">
                <span>Balance:</span> <span>Rs. {val[8]}</span>
            </div>
            <hr style="border-top: 1px dashed black;">
            <div style="text-align: center; font-size: 10px;">Software by BioCloud AI</div>
        </div>
    """, unsafe_allow_html=True)
    st.button("🖨️ Print Receipt", key=f"print_{val[0]}", on_click=lambda: st.write("Browser ka Print (Ctrl+P) use karein"))

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="BioCloud Lab Pro", layout="wide", page_icon="🧪")

# --- 3. SESSION STATE ---
if 'temp_tests' not in st.session_state:
    st.session_state.temp_tests = [] 
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'show_slip' not in st.session_state:
    st.session_state.show_slip = None

def check_login(u, p):
    if u == "admin" and p == "lab786":
        st.session_state['auth'] = True
        st.rerun()
    else:
        st.error("Invalid Username or Password")

# --- 4. AUTH CHECK ---
if not st.session_state['auth']:
    show_login_page(check_login)
else:
    local_css("style.css")
    
    df = get_full_data()
    today = str(datetime.now().date())
    required_cols = ["ID", "Date", "Name", "Age", "Gender", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]

    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🧪 BioCloud Pro</h1>", unsafe_allow_html=True)
        
        if not df.empty and 'Date' in df.columns:
            cash_df = df[df['Date'] == today]
            total_cash = pd.to_numeric(cash_df['Paid_Amount'], errors='coerce').sum()
            total_dues = pd.to_numeric(cash_df['Remaining'], errors='coerce').sum()
        else:
            total_cash, total_dues = 0, 0
            
        st.metric("Aaj Ka Cash", f"Rs. {total_cash}")
        st.metric("Aaj Ke Dues", f"Rs. {total_dues}")
        
        st.divider()
        menu = st.radio("Navigation", ["Registration", "Dues & Reports", "Excel History"])
        if st.button("Logout"):
            st.session_state['auth'] = False
            st.rerun()

    if menu == "Registration":
        st.header("New Patient Registration")
        
        if st.session_state.show_slip:
            st.success("✅ Record Saved!")
            show_receipt(st.session_state.show_slip)
            if st.button("Register Another Patient"):
                st.session_state.show_slip = None
                st.rerun()
            st.divider()

        tdf = get_tests_list()
        test_options = sorted(tdf["Test_Name"].unique().tolist()) if not tdf.empty else []
        test_rate_dict = dict(zip(tdf["Test_Name"], tdf["Rate"])) if not tdf.empty else {}

        with st.expander("➕ Add New Test Type to System", expanded=False):
            c_n1, c_n2, c_n3 = st.columns([2, 1, 1])
            new_t_name = c_n1.text_input("New Test Name")
            new_t_rate = c_n2.number_input("Standard Rate", 0)
            if c_n3.button("Save New Test"):
                if new_t_name:
                    save_test_local(pd.DataFrame([{"Test_Name": new_t_name, "Rate": new_t_rate}]))
                    st.success(f"Test '{new_t_name}' Added!")
                    st.rerun()

        with st.expander("Patient Information", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            p_name = c1.text_input("Patient Name")
            p_age = c2.number_input("Age", 1, 120, value=25)
            p_gender = c3.selectbox("Gender", ["Male", "Female", "Other"])

        st.subheader("Add Tests to Bill")
        col_t1, col_t2, col_t3 = st.columns([2, 1, 1])
        selected_t = col_t1.selectbox("Select Test", ["--- Select ---"] + test_options)
        default_rate = int(test_rate_dict.get(selected_t, 0)) if selected_t != "--- Select ---" else 0
        entered_rate = col_t2.number_input("Rate (Rs.)", value=default_rate, key="rate_input")

        if col_t3.button("➕ Add Test"):
            if selected_t != "--- Select ---":
                st.session_state.temp_tests.append({"Test": selected_t, "Rate": entered_rate})
                st.rerun()

        if st.session_state.temp_tests:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            total_bill = sum(t['Rate'] for t in st.session_state.temp_tests)
            for i, t in enumerate(st.session_state.temp_tests):
                st.write(f"{i+1}. ✅ {t['Test']} --- Rs. {t['Rate']}")
            st.divider()
            st.write(f"**Total Bill: Rs. {total_bill}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            paid_amt = st.number_input("Paid Amount", 0)
            if st.button("💾 Final Save Record", use_container_width=True):
                if p_name and st.session_state.temp_tests:
                    all_tests_str = ", ".join([t['Test'] for t in st.session_state.temp_tests])
                    rem = total_bill - paid_amt
                    new_id = len(df) + 1
                    new_row = [new_id, today, p_name, p_age, p_gender, all_tests_str, total_bill, paid_amt, rem, "-", "-", ("Paid" if rem<=0 else "Pending")]
                    
                    save_record_local(pd.DataFrame([new_row], columns=required_cols))
                    st.session_state.show_slip = new_row 
                    st.session_state.temp_tests = [] 
                    st.rerun()

    elif menu == "Dues & Reports":
        st.header("Update Records & Results")
        if not df.empty:
            pending_df = df[(df["Remaining"] > 0) | (df["Result"] == "-")]
            if not pending_df.empty:
                st.markdown('<div class="login-card">', unsafe_allow_html=True)
                sel_patient = st.selectbox("Search Patient", pending_df["Name"].tolist())
                p_data = df[df["Name"] == sel_patient].iloc[-1]
                
                st.info(f"Test: {p_data['Test']} | Total Bill: {p_data['Total_Bill']} | Already Paid: {p_data['Paid_Amount']}")
                st.warning(f"Remaining Dues: Rs. {p_data['Remaining']}")
                
                c_a, c_b = st.columns(2)
                add_p = c_a.number_input("Add More Payment", 0)
                res_v = c_b.text_input("Enter Result", value=p_data['Result'])
                
                if st.button("Update & Save Record"):
                    new_paid = p_data["Paid_Amount"] + add_p
                    new_rem = p_data["Total_Bill"] - new_paid
                    df.loc[df["ID"] == p_data["ID"], ["Paid_Amount", "Remaining", "Status", "Result"]] = [new_paid, new_rem, ("Paid" if new_rem<=0 else "Pending"), res_v]
                    df.to_csv(PATIENT_FILE, index=False)
                    st.success("Updated Successfully!")
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("No pending records found!")

    elif menu == "Excel History":
        st.header("📊 Lab Database History")
        
        # --- NEW: PRINT OLD SLIPS SECTION ---
        with st.expander("🖨️ Reprint Old Receipt", expanded=False):
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            if not df.empty:
                patient_list = df["Name"].tolist()
                selected_for_print = st.selectbox("Select Patient to Reprint Slip", ["-- Select --"] + patient_list)
                if selected_for_print != "-- Select --":
                    p_to_print = df[df["Name"] == selected_for_print].iloc[-1]
                    show_receipt(p_to_print)
            else:
                st.write("No data available.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.divider()
        
        search_query = st.text_input("🔍 Search History (Name, ID, Date, or Test)")
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)