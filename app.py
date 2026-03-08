import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# १. पेज सेटअप
st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# डेटा सुरक्षितपणे नंबरमध्ये बदलण्यासाठी फंक्शन
def safe_int(val, default=0):
    try:
        if val == '' or val is None: 
            return default
        return int(float(val))
    except:
        return default

# २. गुगल शीट कनेक्शन
def get_client():
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        creds_info = st.secrets["connections"]["gsheets"]
    else:
        creds_info = dict(st.secrets)
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

def load_data():
    client = get_client()
    sheet_id = "1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc"
    workbook = client.open_by_key(sheet_id)
    sheet1 = workbook.get_worksheet(0)
    data = sheet1.get_all_records()
    df = pd.DataFrame(data)
    # कॉलमची नावं स्वच्छ करणे
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df, workbook, sheet1

def main():
    try:
        df, workbook, sheet1 = load_data()
    except Exception as e:
        st.error(f"शीटला कनेक्ट करता आले नाही: {e}")
        return

    st.sidebar.title("🚩 विश्वजीत क्लासेस")
    choice = st.sidebar.selectbox("मेनू निवडा", ["विद्यार्थी लॉगिन", "Admin Panel"])

    # --- विद्यार्थी लॉगिन विभाग ---
    if choice == "विद्यार्थी लॉगिन":
        st.header("🎓 विद्यार्थी पोर्टल")
        if 'student_id' in df.columns:
            data_dict = df.set_index('student_id').to_dict('index')
            
            if "logged_in" not in st.session_state:
                st.session_state["logged_in"] = False

            if not st.session_state["logged_in"]:
                sid = st.text_input("विद्यार्थी ID")
                pwd = st.text_input("पासवर्ड", type="password")
                if st.button("लॉगिन"):
                    if sid in data_dict and str(data_dict[sid].get("password")) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[sid]
                        st.rerun()
                    else:
                        st.error("चुकीचा ID किंवा पासवर्ड!")
            else:
                info = st.session_state["info"]
                st.title(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
                
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    st.image(info.get('photo_url', "https://via.placeholder.com/150"), width=150)
                
                with col_info:
                    st.subheader("📊 माझी प्रगती")
                    c1, c2 = st.columns(2)
                    c1.metric("Abacus Level", info.get('abacus_level', 'N/A'))
                    c2.metric("Vedic Math", info.get('vedic_level', 'N/A'))

                st.divider()
                st.subheader("💰 फी तपशील")
                with st.container(border=True):
                    f1, f2, f3 = st.columns(3)
                    t_val = safe_int(info.get('total_fees'), 6000)
                    p_val = safe_int(info.get('paid_fees'), 0)
                    r_val = t_val - p_val
                    
                    f1.metric("एकूण फी", f"₹{t_val}")
                    f2.metric("भरलेली फी", f"₹{p_val}")
                    f3.metric("बाकी फी", f"₹{r_val}", delta=f"-₹{r_val}" if r_val > 0 else "Clear", delta_color="inverse")

                if st.sidebar.button("Logout"):
                    st.session_state["logged_in"] = False
                    st.rerun()
        else:
            st.error("शीटमध्ये 'student_id' कॉलम सापडला नाही!")

    # --- ADMIN PANEL विभाग ---
    elif choice == "Admin Panel":
        st.header("🛠️ Admin Control Center")
        admin_pwd = st.sidebar.text_input("Admin Password", type="password")
        
        if admin_pwd == "VISHWA_ADMIN_123":
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ नवीन विद्यार्थी", "📝 हजेरी", "📊 विद्यार्थी यादी", "🔄 फी अपडेट", "💰 फी रिपोर्ट"])
            
            with tab1:
                st.subheader("नवीन नोंदणी")
                with st.form("add_student_form", clear_on_submit=True):
                    new_sid = st.text_input("विद्यार्थी ID")
                    new_name = st.text_input("पूर्ण नाव")
                    new_pwd = st.text_input("पासवर्ड", value="12345")
                    new_photo = st.text_input("फोटो URL")
                    new_addr = st.text_area("पत्ता")
                    
                    c1, c2 = st.columns(2)
                    new_abacus = c1.selectbox("Abacus Level", ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "None"])
                    new_vedic = c2.selectbox("Vedic Math", ["Level 1", "Level 2", "Level 3", "None"])
                    
                    st.write("---")
                    cf1, cf2 = st.columns(2)
                    in_total = cf1.number_input("एकूण फी (Total)", min_value=0, value=6000)
                    in_paid = cf2.number_input("भरलेली फी (Paid)", min_value=0, value=0)
                    
                    submitted = st.form_submit_button("विद्यार्थी सेव्ह करा")
                    
                    if submitted:
                        if new_sid and new_name:
                            try:
                                in_rem = in_total - in_paid
                                sheet1.append_row([
                                    new_sid, new_pwd, new_name, new_photo, new_addr, 
                                    new_abacus, new_vedic, "0", in_total, in_paid, in_rem, "नवीन प्रवेश"
                                ])
                                st.success(f"✅ {new_name} ची नोंदणी यशस्वी!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        else:
                            st.warning("ID आणि नाव आवश्यक आहे!")

            with tab2:
                st.subheader("हजेरी मार्क करा")
                if 'student_id' in df.columns:
                    target_sid = st.selectbox("विद्यार्थी निवडा (ID)", df['student_id'].tolist())
                    status = st.radio("स्थिती", ["Present", "Absent", "Holiday"], horizontal=True)
                    if st.button("Save Attendance"):
                        try:
                            log_sheet = workbook.worksheet("attendance_logs")
                            log_sheet.append_row([target_sid, str(datetime.now().date()), status])
                            st.success(f"✅ {target_sid} ची हजेरी सेव्ह झाली!")
                        except:
                            st.error("'attendance_logs' शीट सापडली नाही!")

            with tab3:
                st.subheader("सर्व विद्यार्थी माहिती")
                st.dataframe(df, use_container_width=True)

            with tab4:
                st.subheader("🔄 विद्यार्थ्याची फी अपडेट करा")
                if not df.empty and 'name' in df.columns:
                    student_to_update = st.selectbox("विद्यार्थी निवडा", df['name'].tolist(), key="fee_update_select")
                    s_row = df[df['name'] == student_to_update].iloc[0]
                    
                    with st.container(border=True):
                        u_col1, u_col2 = st.columns(2)
                        u_total = u_col1.number_input("Total Fees", value=safe_int(s_row.get('total_fees'), 6000))
                        u_paid = u_col2.number_input("Paid Amount", value=safe_int(s_row.get('paid_fees'), 0))
                        
                        u_rem = u_total - u_paid
                        st.info(f"बाकी फी: ₹{u_rem}")
                        
                        if st.button("Update Fee Records"):
                            try:
                                cell = sheet1.find(str(s_row['student_id']))
                                # कॉलम नंबर तुमच्या शीटनुसार तपासा
                                sheet1.update_cell(cell.row, 9, u_total)
                                sheet1.update_cell(cell.row, 10, u_paid)
                                sheet1.update_cell(cell.row, 11, u_rem)
                                st.success(f"✅ {student_to_update} चा हिशोब अपडेट झाला!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"अपडेट करताना चूक झाली: {e}")

            with tab5:
                st.subheader("💰 संपूर्ण फी अहवाल (Fee Report)")
                if not df.empty:
                    # 'remaining_fees' कॉलम नसल्यास ऑन-द-फ्लाय कॅल्क्युलेशन करणे
                    t_fees = df['total_fees'].apply(safe_int) if 'total_fees' in df.columns else pd.Series([0]*len(df))
                    p_fees = df['paid_fees'].apply(safe_int) if 'paid_fees' in df.columns else pd.Series([0]*len(df))
                    r_fees = t_fees - p_fees
                    
                    total_collected = p_fees.sum()
                    total_pending = r_fees.sum()
                    paid_count = (r_fees <= 0).sum()
                    unpaid_count = (r_fees > 0).sum()
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Paid Students", paid_count)
                    m2.metric("Unpaid Students", unpaid_count)
                    m3.metric("Total Collected", f"₹{total_collected}")
                    m4.metric("Total Remaining", f"₹{total_pending}", delta_color="inverse")
                    
                    st.divider()
                    st.write("### 📝 विद्यार्थ्यांनुसार फी तपशील")
                    report_df = pd.DataFrame({
                        'विद्यार्थ्याचे नाव': df['name'] if 'name' in df.columns else "N/A",
                        'एकूण फी': t_fees,
                        'भरलेली फी': p_fees,
                        'शिल्लक फी': r_fees
                    })
                    st.table(report_df)

        elif admin_pwd:
            st.error("पासवर्ड चुकीचा आहे!")

if __name__ == "__main__":
    main()
