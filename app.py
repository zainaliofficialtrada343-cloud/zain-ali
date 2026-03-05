import streamlit as st
import pandas as pd
import os
from datetime import datetime
from login_ui import show_login_page, local_css
from receipt_design import show_receipt

# --- 1. CSV DATABASE CONFIG ---
PATIENT_FILE = "data_db.csv"
TESTS_FILE = "tests_db.csv"
EXPENSE_FILE = "expenses_db.csv" 

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

def get_expense_data():
    if os.path.exists(EXPENSE_FILE):
        df = pd.read_csv(EXPENSE_FILE)
        df['Date'] = pd.to_datetime(df['Date']).dt.date # Fixed date format for math
        return df
    else:
        return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])

def save_record_local(new_row_df):
    existing_data = get_full_data()
    updated_data = pd.concat([existing_data, new_row_df], ignore_index=True)
    updated_data.to_csv(PATIENT_FILE, index=False)

def save_test_local(new_test_df):
    existing_tests = get_tests_list()
    updated_tests = pd.concat([existing_tests, new_test_df], ignore_index=True)
    updated_tests.to_csv(TESTS_FILE, index=False)

# --- 3. PAGE CONFIG ---
st.set_page_config(page_title="BioCloud Lab Pro", layout="wide", page_icon="🧪")

# --- 4. SESSION STATE & LOGIN ---
if 'temp_tests' not in st.session_state: st.session_state.temp_tests = [] 
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'show_slip' not in st.session_state: st.session_state.show_slip = None
if 'saved_mobile' not in st.session_state: st.session_state.saved_mobile = ""
if 'lab_name' not in st.session_state: st.session_state.lab_name = "MAJEED COLONY SEC 2, KARACHI"
if 'lab_phone' not in st.session_state: st.session_state.lab_phone = "03XX-XXXXXXX"

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

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                        url("https://raw.githubusercontent.com/zainaliofficialtrada343-cloud/BioCloud_/main/lab_girl.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    df = get_full_data()
    today_dt = datetime.now().date()
    today = str(today_dt)
    required_cols = ["ID", "Invoice", "Date", "Name", "Mobile", "Age", "Gender", "Collected", "Test", "Total_Bill", "Paid_Amount", "Remaining", "Result", "Unit", "Status"]

    with st.sidebar:
        st.markdown("<h1 style='text-align: center;'>🧪 BioCloud Pro</h1>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("Navigation", ["Registration", "Dues & Reports", "Expense Manager", "History Search", "Excel History", "⚙️ Lab Settings"])
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
            # Auto Sequence Invoice
            inv_seq = f"INV-{len(df) + 101}"
            p_inv = r1c3.text_input("Invoice #", value=inv_seq)
            
            r2c1, r2c2, r2c3, r2c4 = st.columns([1, 1, 1, 1])
            p_age = r2c1.number_input("Age", 1, 120, value=25)
            p_gender = r2c2.selectbox("Gender", ["Male", "Female", "Other"])
            p_ref = r2c3.text_input("Doctor / Ref By", value="Self")
            p_coll = r2c4.selectbox("Collected From", ["Lab Box", "Home", "Hospital"]) # Wapas add kar diya

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
            # Validation: Paid amount cannot exceed total bill
            paid_amt = st.number_input("Paid Amount", 0, max_value=int(total_bill))
            
            if st.button("💾 Final Save Record", use_container_width=True):
                if p_name and st.session_state.temp_tests:
                    all_tests_str = ", ".join([t['Test'] for t in st.session_state.temp_tests])
                    rem = total_bill - paid_amt
                    new_id = len(df) + 1
                    # Collected field update
                    data_list = [new_id, p_inv, today, p_name, p_mobile, p_age, p_gender, p_coll, all_tests_str, total_bill, paid_amt, rem, "-", "-", ("Paid" if rem<=0 else "Pending")]
                    save_record_local(pd.DataFrame([data_list], columns=required_cols))
                    st.session_state.show_slip = data_list 
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

    elif menu == "Expense Manager":
        st.header("💸 Kharcha Pani (Expense Manager)")
        ex_df = get_expense_data()
        tab1, tab2 = st.tabs(["➕ Add Expense", "📊 Expense Reports"])
        with tab1:
            with st.expander("Enter New Expense Details", expanded=True):
                e_cat = st.selectbox("Category", ["Staff Salary", "Chemicals/Kits", "Rent/Bills", "Tea/Food", "Other"])
                e_desc = st.text_input("Description")
                e_amt = st.number_input("Amount", 0)
                if st.button("Save Expense"):
                    new_ex = pd.DataFrame([[today_dt, e_cat, e_desc, e_amt]], columns=["Date", "Category", "Description", "Amount"])
                    pd.concat([ex_df, new_ex], ignore_index=True).to_csv(EXPENSE_FILE, index=False)
                    st.success("Expense Saved!")
                    st.rerun()
        with tab2:
            st.subheader("Filter Expenses")
            f_col1, f_col2 = st.columns(2)
            view_type = f_col1.selectbox("View By", ["Daily", "Monthly", "Yearly", "All Time"])
            if not ex_df.empty:
                # Proper date comparison
                ex_df['Date'] = pd.to_datetime(ex_df['Date']).dt.date
                if view_type == "Daily": filtered_ex = ex_df[ex_df['Date'] == today_dt]
                elif view_type == "Monthly": filtered_ex = ex_df[pd.to_datetime(ex_df['Date']).dt.month == today_dt.month]
                elif view_type == "Yearly": filtered_ex = ex_df[pd.to_datetime(ex_df['Date']).dt.year == today_dt.year]
                else: filtered_ex = ex_df
                total_ex = filtered_ex['Amount'].sum()
                st.markdown(f"### Total Expense ({view_type}): **Rs. {total_ex}**")
                st.dataframe(filtered_ex, use_container_width=True)
            else: st.info("Abhi tak koi kharcha add nahi kiya gaya.")

    elif menu == "History Search":
        st.header("🔍 Advanced Patient Search")
        search_mobile = st.text_input("Enter Patient Mobile Number to see History")
        if search_mobile:
            hist = df[df['Mobile'].astype(str).str.contains(search_mobile)]
            if not hist.empty:
                st.write(f"Found {len(hist)} records for this number:")
                st.dataframe(hist, use_container_width=True)
            else: st.warning("No record found for this number.")

    elif menu == "Excel History":
        st.header("📊 Lab Database History")
        with st.expander("🖨️ Reprint Old Slip (Smart Search)", expanded=True):
            if not df.empty:
                search_term = st.text_input("Search by Name, Mobile or Invoice #")
                if search_term:
                    filtered_search = df[df['Name'].str.contains(search_term, case=False) | df['Mobile'].astype(str).str.contains(search_term) | df['Invoice'].str.contains(search_term, case=False)]
                    if not filtered_search.empty:
                        options = filtered_search.apply(lambda x: f"{x['Name']} | {x['Invoice']} | {x['Date']}", axis=1).tolist()
                        selected_option = st.selectbox("Select Patient to Print", ["-- Select --"] + options)
                        if selected_option != "-- Select --":
                            idx = options.index(selected_option)
                            p_to_print = filtered_search.iloc[idx]
                            show_receipt(p_to_print.tolist())
                    else: st.warning("No matching patient found.")
        st.divider()
        search_query = st.text_input("🔍 Search History Table")
        if search_query:
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else: st.dataframe(df, use_container_width=True, hide_index=True)

    elif menu == "⚙️ Lab Settings":
        st.header("⚙️ Lab System Settings & Reports")
        
        # Cash Counter with Expense Link
        st.subheader("💰 Aaj Ki Cash & Profit Report")
        ex_df = get_expense_data()
        today_ex = ex_df[ex_df['Date'] == today_dt]['Amount'].sum() if not ex_df.empty else 0
        
        if not df.empty and 'Date' in df.columns:
            cash_df = df[df['Date'] == today]
            total_cash = pd.to_numeric(cash_df['Paid_Amount'], errors='coerce').sum()
            total_dues = pd.to_numeric(cash_df['Remaining'], errors='coerce').sum()
            net_profit = total_cash - today_ex
        else: 
            total_cash, total_dues, net_profit = 0, 0, 0
        
        stat_c1, stat_c2, stat_c3 = st.columns(3)
        stat_c1.metric("Aaj Ka Kul Cash", f"Rs. {total_cash}")
        stat_c2.metric("Aaj Ka Kharcha", f"Rs. {today_ex}")
        stat_c3.metric("Net Profit (Cash-Exp)", f"Rs. {net_profit}")
        
        st.divider()
        # Backup Button
        st.subheader("📥 Data Backup (Excel)")
        if not df.empty:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Full Patient History", data=csv_data, file_name=f"Lab_Backup_{today}.csv", mime='text/csv')

        st.divider()
        # Lab Info Section
        st.subheader("📍 Update Lab Information")
        c1, c2 = st.columns(2)
        new_lab_name = c1.text_input("Lab Address / Name", value=st.session_state.lab_name)
        new_lab_phone = c2.text_input("Lab Contact No.", value=st.session_state.lab_phone)
        
        if st.button("Update Lab Settings"):
            st.session_state.lab_name = new_lab_name
            st.session_state.lab_phone = new_lab_phone
            st.success("Lab details updated successfully!")
            st.rerun()