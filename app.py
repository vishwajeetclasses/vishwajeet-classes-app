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
            tab1, tab2 = st.tabs(["हजेरी भरा", "विद्यार्थी यादी"])
            
            with tab1:
                st.subheader("हजेरी मार्क करा")
                target_sid = st.selectbox("विद्यार्थी निवडा", df['student_id'].tolist())
                status = st.radio("स्थिती", ["Present", "Absent", "Holiday", "Emergency"])
                if st.button("Save Attendance"):
                    # attendance_logs शीटमध्ये डेटा लिहिणे
                    try:
                        log_sheet = workbook.worksheet("attendance_logs")
                        log_sheet.append_row([target_sid, str(datetime.now().date()), status])
                        st.success("हजेरी सेव्ह झाली!")
                    except:
                        st.error("'attendance_logs' नावाची शीट सापडली नाही!")
            
            with tab2:
                st.dataframe(df)
        elif admin_pwd:
            st.error("चुकीचा पासवर्ड!")

if __name__ == "__main__":
    main()

