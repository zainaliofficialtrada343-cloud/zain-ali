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

# --- 2. CLEAN RECEIPT FUNCTION (FIXED FOR 80mm PRINTING) ---
def show_receipt(val):
    v = val.tolist() if hasattr(val, 'tolist') else val
    try:
        # Improved CSS: Is se sirf receipt box print hoga, baki screen blank rahegi
        receipt_html = f"""
        <style>
            @media print {{
                /* Hide everything except the receipt box */
                body * {{ visibility: hidden; }}
                .receipt-box, .receipt-box * {{ visibility: visible; }}
                .receipt-box {{ 
                    position: absolute; 
                    left: 0; 
                    top: 0; 
                    width: 80mm; 
                    border: none !important; 
                }}
                /* Remove Streamlit default spacing */
                .main .block-container {{ padding: 0 !important; }}
            }}
            .receipt-box {{
                width: 72mm; /* Better fit for 80mm roll */
                padding: 5px;
                font-family: 'Courier New', Courier, monospace;
                border: 1px dashed #000;
                background-color: #fff;
                color: #000;
                margin: 10px auto;
            }}
            .r-bold {{ font-weight: bold; font-size: 16px; text-transform: uppercase; }}
            .r-header {{ text-align: center; margin-bottom: 8px; border-bottom: 1px solid #000; padding-bottom: 5px; }}
            .r-text {{ font-size: 12px; margin: 2px 0; }}
            .r-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }}
            .r-table th {{ border-bottom: 1px dashed #000; text-align: left; }}
            .r-total {{ border-top: 1px solid #000; margin-top: 8px; padding-top: 5px; font-weight: bold; }}
        </style>

        <div class="receipt-box">
            <div class="r-header">
                <div class="r-bold">( THE LIFE CARE )</div>
                <div class="r-text">MAJEED COLONY SEC 2, KARACHI</div>
                <div class="r-text">0370-2906075</div>
            </div>
            
            <div class="r-text"><b>Inv:</b> {v[1]} <span style="float:right;"><b>Date:</b> {v[2]}</span></div>
            <div class="r-text"><b>Name:</b> {v[3]}</div>
            <div class="r-text"><b>Age/Gen:</b> {v[5]} / {v[6]}</div>
            <div class="r-text"><b>Mobile:</b> {v[4]}</div>
            <hr style="border-top: 1px dashed #000;">

            <table class="r-table">
                <thead>
                    <tr><th>Description</th><th style="text-align:center;">Qty</th><th style="text-align:right;">Amt</th></tr>
                </thead>
                <tbody>
        """
        
        tests_list = str(v[8]).split(", ")
        for t in tests_list:
            receipt_html += f"<tr><td>{t}</td><td style='text-align:center;'>1</td><td style='text-align:right;'>-</td></tr>"

        receipt_html += f"""
                </tbody>
            </table>
            
            <div class="r-total">
                <div class="r-text">TOTAL BILL: <span style="float:right;">Rs. {v[9]}</span></div>
                <div class="r-text">PAID AMOUNT: <span style="float:right;">Rs. {v[10]}</span></div>
                <div class="r-text" style="font-size: 14px;">BALANCE: <span style="float:right;">Rs. {v[11]}</span></div>
            </div>
            
            <div style="text-align:center; margin-top:15px; font-size:10px; border-top: 1px solid #000; padding-top: 5px;">
                Developed by Zain - 03702906075<br>*** Software System ***
            </div>
        </div>
        """
        
        st.markdown(receipt_html, unsafe_allow_html=True)
        st.button("Print Slip (Ctrl+P)", help="Click and then press Ctrl+P on keyboard")
            
    except Exception as e:
        st.error(f"Slip display karne mein masla: {e}")

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="BioCloud Lab Pro", layout="wide", page_icon="🧪")

# --- 4. SESSION STATE & LOGIN ---
if 'temp_tests' not in st.session_state: st.session_state.temp_tests = [] 
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'show_slip' not in st.session_state: st.session_state.show_slip = None
if 'saved_mobile' not in st.session_state: st.session_state.saved_mobile = ""

def check_login(u, p):
    if u == "admin" and p == "lab786":
        st.session_state['auth'] = True
        st.rerun()
    else: st.error("Invalid Username or Password")

# --- 5. MAIN APP LOGIC ---
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
            st.markdown("### Selected Tests")
            for i, t in enumerate(st.session_state.temp_tests):
                cols = st.columns([4, 1])
                cols[0].write(f"{i+1}. ✅ {t['Test']} --- Rs. {t['Rate']}")
                if cols[1].button("❌", key=f"del_{i}"):
                    st.session_state.temp_tests.pop(i)
                    st.rerun()
            
            total_bill = sum(t['Rate'] for t in st.session_state.temp_tests)
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
            pending_df = df[df["Status"] == "Pending"]
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
            else:
                st.info("Koi Pending record nahi hai.")

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