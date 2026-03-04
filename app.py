import streamlit as st
import pandas as pd
import os
from datetime import datetime
from login_ui import show_login_page, local_css

# --- 1. CSV DATABASE CONFIG ---
PATIENT_FILE = "data_db.csv"
TESTS_FILE = "tests_db.csv"

def get_full_data():
    cols = ["ID", "Invoice", "Date", "Name", "Mobile", "Age", "Gender", "Collected", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]
    if os.path.exists(PATIENT_FILE):
        df = pd.read_csv(PATIENT_FILE)
        for c in cols:
            if c not in df.columns:
                df[c] = "-"
        return df
    else:
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

# --- 100% MATCHED SLIP DESIGN ---
def show_receipt(data):
    val = data.tolist() if hasattr(data, 'tolist') else data
    
    st.markdown("""
        <style>
        @media print {
            header, footer, .stSidebar, .stButton, .stSelectbox, .stTextInput, .stNumberInput, [data-testid="stExpander"] {
                display: none !important;
            }
            .print-container { border: none !important; width: 100% !important; margin: 0 !important; padding: 0 !important; }
        }
        .print-container {
            background-color: #fff; padding: 20px;
            width: 400px; color: #000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0 auto; border: 1px solid #eee;
        }
        .main-title { text-align: center; font-weight: 900; font-size: 26px; margin: 0; text-transform: uppercase; letter-spacing: 1px; }
        .sub-title { text-align: center; font-weight: bold; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .patient-slip-bar { 
            text-align: center; font-weight: bold; border-top: 3px solid #000; 
            border-bottom: 3px solid #000; background: #fff; margin: 5px 0; padding: 2px 0; font-size: 18px;
        }
        .info-table { width: 100%; border-bottom: 2px dashed #000; margin-bottom: 10px; font-size: 15px; line-height: 1.2; }
        .test-table { width: 100%; border-collapse: collapse; font-size: 15px; margin-top: 5px; }
        .test-table th { border-bottom: 2px solid #000; text-align: left; padding: 8px 0; font-weight: bold; }
        .test-table td { padding: 6px 0; border-bottom: 1px solid #f0f0f0; }
        .total-section { border-top: 3px solid #000; margin-top: 10px; padding-top: 5px; }
        .total-section table { width: 100%; font-weight: bold; font-size: 18px; }
        .dev-tag { text-align: center; margin-top: 30px; font-size: 12px; border-top: 1px solid #ccc; padding-top: 5px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # Clean test string and handle split
    test_str = str(val[8]) if val[8] and not pd.isna(val[8]) else "-"
    test_names = test_str.split(", ")
    
    test_rows_html = ""
    for i, tname in enumerate(test_names, 1):
        test_rows_html += f"<tr><td>{i}</td><td>{tname}</td><td>-</td><td>1</td><td style='text-align:right;'>-</td></tr>"

    receipt_html = f"""
        <div class="print-container">
            <div class="main-title">JAWAD MEDICAL CENTERE</div>
            <div class="sub-title">MAJEED COLONY SEC 2</div>
            <div class="patient-slip-bar">PATIENT SLIP</div>
            <table class="info-table">
                <tr><td><b>Slip No:</b> {val[1]}</td><td style="text-align:right;">{val[2]}</td></tr>
                <tr><td><b>Shift:</b> Evening</td><td style="text-align:right;"></td></tr>
                <tr><td colspan="2" style="padding-top:10px;"><b>Patient:</b> <span style="float:right;"><b>{val[3]}</b></span></td></tr>
                <tr><td><b>Cell/Gen/Age:</b></td><td style="text-align:right;">({str(val[6])[0] if val[6] else '?'}/{val[5]})</td></tr>
                <tr><td><b>Ref By:</b></td><td style="text-align:right;">SELF</td></tr>
                <tr><td><b>Doctor:</b></td><td style="text-align:right;">DR. ZAIN</td></tr>
            </table>
            <table class="test-table">
                <thead><tr><th>S#</th><th>CHARGES</th><th>Rate</th><th>Qty</th><th style="text-align:right;">AMT</th></tr></thead>
                <tbody>{test_rows_html}</tbody>
            </table>
            <div class="total-section">
                <table>
                    <tr><td>TOTAL:</td><td style="text-align:right;">{val[9]}</td></tr>
                    <tr><td>RECEIVED:</td><td style="text-align:right;">{val[10]}</td></tr>
                    <tr style="font-size: 20px;"><td>BALANCE:</td><td style="text-align:right;">{val[11]}</td></tr>
                </table>
            </div>
            <div class="dev-tag">
                Developed by zain 03702906075
            </div>
        </div>
    """
    st.markdown(receipt_html, unsafe_allow_html=True)
    if st.button("🖨️ Print Now", key=f"btn_{val[1]}_{val[0]}"):
        st.info("Keyboard se **Ctrl + P** dabayein.")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="BioCloud Lab Pro", layout="wide", page_icon="🧪")

# --- 3. SESSION STATE ---
if 'temp_tests' not in st.session_state: st.session_state.temp_tests = [] 
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'show_slip' not in st.session_state: st.session_state.show_slip = None
if 'saved_mobile' not in st.session_state: st.session_state.saved_mobile = ""

def check_login(u, p):
    if u == "admin" and p == "lab786":
        st.session_state['auth'] = True
        st.rerun()
    else: st.error("Invalid Username or Password")

# --- 4. AUTH CHECK ---
if not st.session_state['auth']:
    show_login_page(check_login)
else:
    local_css("style.css")
    df = get_full_data()
    today = str(datetime.now().date())
    required_cols = ["ID", "Invoice", "Date", "Name", "Mobile", "Age", "Gender", "Collected", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]

    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🧪 BioCloud Pro</h1>", unsafe_allow_html=True)
        if not df.empty and 'Date' in df.columns:
            cash_df = df[df['Date'] == today]
            total_cash = pd.to_numeric(cash_df['Paid_Amount'], errors='coerce').sum()
            total_dues = pd.to_numeric(cash_df['Remaining'], errors='coerce').sum()
        else: total_cash, total_dues = 0, 0
        st.metric("Aaj Ka Cash", f"Rs. {total_cash}")
        st.metric("Aaj Ke Dues", f"Rs. {total_dues}")
        st.divider()
        menu = st.radio("Navigation", ["Registration", "Dues & Reports", "Excel History"])
        
        st.divider()
        # --- DELETE ALL DATA FEATURE ---
        if st.checkbox("Enable Delete Option"):
            if st.button("⚠️ Delete All Patient Data", type="primary"):
                if os.path.exists(PATIENT_FILE):
                    os.remove(PATIENT_FILE)
                    st.success("Sabh data delete ho gaya!")
                    st.rerun()

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

        with st.expander("➕ Add New Test Type"):
            c_n1, c_n2, c_n3 = st.columns([2, 1, 1])
            new_t_name = c_n1.text_input("New Test Name")
            new_t_rate = c_n2.number_input("Standard Rate", 0)
            if c_n3.button("Save New Test"):
                if new_t_name:
                    save_test_local(pd.DataFrame([{"Test_Name": new_t_name, "Rate": new_t_rate}]))
                    st.success("Test Added!")
                    st.rerun()

        with st.expander("Patient Information", expanded=True):
            r1c1, r1c2, r1c3 = st.columns([2, 1, 1])
            p_name = r1c1.text_input("Patient Name")
            p_mobile = r1c2.text_input("Mobile No", value=st.session_state.saved_mobile)
            st.session_state.saved_mobile = p_mobile
            p_inv = r1c3.text_input("Invoice #", value=f"INV-{datetime.now().strftime('%H%M%S')}")
            r2c1, r2c2, r2c3 = st.columns([1, 1, 2])
            p_age = r2c1.number_input("Age", 1, 120, value=25)
            p_gender = r2c2.selectbox("Gender", ["Male", "Female", "Other"])
            p_coll = r2c3.text_input("Collected From", value="Lab")

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
            total_bill = sum(t['Rate'] for t in st.session_state.temp_tests)
            for i, t in enumerate(st.session_state.temp_tests):
                st.write(f"{i+1}. ✅ {t['Test']} --- Rs. {t['Rate']}")
            paid_amt = st.number_input("Paid Amount", 0)
            if st.button("💾 Final Save Record", use_container_width=True):
                if p_name and st.session_state.temp_tests:
                    all_tests_str = ", ".join([t['Test'] for t in st.session_state.temp_tests])
                    rem = total_bill - paid_amt
                    new_id = len(df) + 1
                    new_row = [new_id, p_inv, today, p_name, p_mobile, p_age, p_gender, p_coll, all_tests_str, total_bill, paid_amt, rem, "-", "-", ("Paid" if rem<=0 else "Pending")]
                    save_record_local(pd.DataFrame([new_row], columns=required_cols))
                    st.session_state.show_slip = new_row 
                    st.session_state.temp_tests = [] 
                    st.rerun()

    elif menu == "Dues & Reports":
        st.header("Update Records & Results")
        if not df.empty:
            pending_df = df[(df["Remaining"] > 0) | (df["Result"] == "-")]
            if not pending_df.empty:
                sel_patient = st.selectbox("Search Patient", pending_df["Name"].tolist())
                p_data = df[df["Name"] == sel_patient].iloc[-1]
                st.info(f"Test: {p_data['Test']} | Dues: Rs. {p_data['Remaining']}")
                c_a, c_b = st.columns(2)
                add_p = c_a.number_input("Add More Payment", 0)
                res_v = c_b.text_input("Enter Result", value=p_data['Result'])
                if st.button("Update & Save Record"):
                    new_paid = p_data["Paid_Amount"] + add_p
                    new_rem = p_data["Total_Bill"] - new_paid
                    df.loc[df["ID"] == p_data["ID"], ["Paid_Amount", "Remaining", "Status", "Result"]] = [new_paid, new_rem, ("Paid" if new_rem<=0 else "Pending"), res_v]
                    df.to_csv(PATIENT_FILE, index=False)
                    st.success("Updated!")
                    st.rerun()

    elif menu == "Excel History":
        st.header("📊 Lab Database History")
        with st.expander("🖨️ Reprint Old Slip"):
            if not df.empty:
                patient_names = df["Name"].tolist()
                selected_p = st.selectbox("Select Patient to Print", ["-- Select --"] + patient_names)
                if selected_p != "-- Select --":
                    p_to_print = df[df["Name"] == selected_p].iloc[-1]
                    show_receipt(p_to_print)
        st.divider()
        search_query = st.text_input("🔍 Search History")
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)