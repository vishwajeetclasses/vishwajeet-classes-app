import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# १. पेज सेटअप
st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# २. गुगल शीट कनेक्शन (gspread Method)
def get_client():
    # १. आधी 'connections' की शोधण्याचा प्रयत्न करणे
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        creds_info = st.secrets["connections"]["gsheets"]
    # २. जर डायरेक्ट JSON पेस्ट केला असेल तर पूर्ण secrets वापरणे
    else:
        creds_info = dict(st.secrets)
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(creds)

def load_data():
    client = get_client()
    # तुमची शीट ID
    sheet_id = "1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc"
    workbook = client.open_by_key(sheet_id)
    
    # Sheet1 (विद्यार्थी डेटा)
    sheet1 = workbook.get_worksheet(0)
    df = pd.DataFrame(sheet1.get_all_records())
    df.columns = [c.strip().lower() for c in df.columns]
    
    return df, workbook

def main():
    try:
        df, workbook = load_data()
    except Exception as e:
        st.error(f"शीटला कनेक्ट करता आले नाही: {e}")
        return

    st.sidebar.title("🚩 विश्वजीत क्लासेस")
    choice = st.sidebar.selectbox("मेनू निवडा", ["विद्यार्थी लॉगिन", "Admin Panel"])

    # --- विद्यार्थी लॉगिन विभाग ---
    if choice == "विद्यार्थी लॉगिन":
        st.header("🎓 विद्यार्थी पोर्टल")
        data_dict = df.set_index('student_id').to_dict('index')
        
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            sid = st.text_input("विद्यार्थी ID")
            pwd = st.text_input("पासवर्ड", type="password")
            if st.button("लॉगिन"):
                if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["info"] = data_dict[sid]
                    st.rerun()
                else:
                    st.error("चुकीचा ID किंवा पासवर्ड!")
        else:
            info = st.session_state["info"]
            st.title(f"नमस्ते, {info['name']}! 👋")
            # फोटो दाखवणे
            st.image(info.get('photo_url', "https://via.placeholder.com/150"), width=150)
            
            col1, col2 = st.columns(2)
            col1.metric("Abacus Level", info.get('abacus_level', 'N/A'))
            col2.metric("Vedic Math", info.get('vedic_level', 'N/A'))
            
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

    # --- ADMIN PANEL विभाग ---
    elif choice == "Admin Panel":
        st.header("🛠️ Admin Control Center")
        admin_pwd = st.sidebar.text_input("Admin Password", type="password")
        
        if admin_pwd == "VISHWA_ADMIN_123":
            # आता आपण ४ टॅब्स करूया
            tab1, tab2, tab3, tab4 = st.tabs(["➕ नवीन विद्यार्थी जोडा", "📝 हजेरी भरा", "📊 विद्यार्थी यादी", "💰 फी स्टेटस"])
            
            # --- टॅब १: नवीन विद्यार्थी जोडा ---
            with tab1:
                st.subheader("नवीन विद्यार्थ्याची नोंदणी")
                with st.form("add_student_form", clear_on_submit=True):
                    new_sid = st.text_input("विद्यार्थी ID (उदा. VC101)")
                    new_name = st.text_input("विद्यार्थ्याचे पूर्ण नाव")
                    new_pwd = st.text_input("लॉगिन पासवर्ड", value="12345")
                    new_photo = st.text_input("फोटो URL (Google Drive/Image link)")
                    new_addr = st.text_area("पत्ता")
                    
                    c1, c2 = st.columns(2)
                    new_abacus = c1.selectbox("Abacus Level", ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "None"])
                    new_vedic = c2.selectbox("Vedic Math Level", ["Level 1", "Level 2", "Level 3", "None"])
                    
                    new_fees = st.selectbox("फी स्टेटस", ["Pending", "Paid"])
                    
                    submitted = st.form_submit_button("विद्यार्थी जोडा")
                    
                    if submitted:
                        if new_sid and new_name:
                            try:
                                # गुगल शीटच्या Sheet1 मध्ये नवीन रांग (Row) जोडणे
                                sheet1 = workbook.get_worksheet(0)
                                # तुमच्या शीटच्या कॉलमच्या क्रमानुसार ही लिस्ट असावी:
                                # student_id, password, name, photo_url, address, abacus_level, vedic_level, attendance_percent, fees, progress_remark
                                sheet1.append_row([
                                    new_sid, new_pwd, new_name, new_photo, new_addr, 
                                    new_abacus, new_vedic, "0", new_fees, "नवीन प्रवेश"
                                ])
                                st.success(f"✅ {new_name} ची नोंदणी यशस्वी झाली!")
                            except Exception as e:
                                st.error(f"एरर आला: {e}")
                        else:
                            st.warning("ID आणि नाव भरणे अनिवार्य आहे!")

            # --- टॅब २: हजेरी भरा ---
            with tab2:
                st.subheader("हजेरी मार्क करा")
                target_sid = st.selectbox("विद्यार्थी निवडा (ID)", df['student_id'].tolist())
                status = st.radio("स्थिती", ["Present", "Absent", "Holiday", "Emergency"], horizontal=True)
                if st.button("Save Attendance"):
                    try:
                        log_sheet = workbook.worksheet("attendance_logs")
                        log_sheet.append_row([target_sid, str(datetime.now().date()), status])
                        st.success(f"✅ {target_sid} साठी {status} हजेरी सेव्ह झाली!")
                    except:
                        st.error("'attendance_logs' नावाची शीट सापडली नाही! कृपया गुगल शीटमध्ये ही टॅब बनवा.")

            # --- टॅब ३: विद्यार्थी यादी ---
            with tab3:
                st.subheader("सर्व विद्यार्थी")
                st.dataframe(df)

            # --- टॅब ४: फी मॅनेजमेंट ---
            with tab4:
                st.subheader("फी रिपोर्ट")
                paid_count = len(df[df['fees'].str.lower() == 'paid'])
                pending_count = len(df[df['fees'].str.lower() == 'pending'])
                
                col_f1, col_f2 = st.columns(2)
                col_f1.metric("Paid Students", paid_count)
                col_f2.metric("Pending Students", pending_count)
                
                st.table(df[['student_id', 'name', 'fees']])

        elif admin_pwd:
            st.error("चुकीचा पासवर्ड!")

if __name__ == "__main__":
    main()


