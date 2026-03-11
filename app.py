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
        
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            if 'student_id' in df.columns:
                data_dict = df.set_index('student_id').to_dict('index')
                sid = st.text_input("विद्यार्थी ID")
                pwd = st.text_input("पासवर्ड", type="password")
                if st.button("लॉगिन"):
                    if sid in data_dict and str(data_dict[sid].get("password")) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[sid]
                        st.session_state["sid"] = sid
                        st.rerun()
                    else:
                        st.error("चुकीचा ID किंवा पासवर्ड!")
        else:
            info = st.session_state.get("info", {})
            current_sid = st.session_state.get("sid", "")
            
            if not current_sid:
                st.session_state["logged_in"] = False
                st.rerun()

            st.title(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            
            # --- निकाल विभाग (Exam Results) ---
            st.divider()
            st.subheader("📝 माझे परीक्षेचे निकाल (Exam Performance)")
            
            try:
                # गुगल शीटमध्ये 'exam_results' नावाची शीट असणे आवश्यक आहे
                exam_sheet = workbook.worksheet("exam_results")
                exam_data = pd.DataFrame(exam_sheet.get_all_records())
                
                my_exams = exam_data[exam_data['student_id'].astype(str) == str(current_sid)].copy()
                
                if not my_exams.empty:
                    # कॅल्क्युलेशन आणि फॉर्मेटिंग
                    def style_exam(row):
                        # वेळ ६ मिनिटांपेक्षा जास्त असेल तर लाल, नाहीतर हिरवा
                        time_val = float(row['time_taken'])
                        color = 'color: green;' if time_val <= 6.0 else 'color: red;'
                        return [color] * len(row)

                    # Accuracy काढणे
                    my_exams['Accuracy (%)'] = (my_exams['correct_ans'] / my_exams['attempted'] * 100).round(2)
                    my_exams['Score (/100)'] = (my_exams['score'] / 100 * 100).round(2) # जर आउट ऑफ १०० असेल तर

                    # दाखवण्यासाठी कॉलम्स निवडणे
                    display_cols = {
                        'exam_id': 'Paper No.',
                        'attempted': 'Attempted',
                        'time_taken': 'Time (Min)',
                        'score': 'Score',
                        'Accuracy (%)': 'Accuracy (%)'
                    }
                    
                    final_exam_df = my_exams[list(display_cols.keys())].rename(columns=display_cols)
                    
                    st.dataframe(final_exam_df.style.apply(lambda x: [
                        'color: green; font-weight: bold' if float(x['Time (Min)']) <= 6.0 else 'color: red; font-weight: bold'
                        for _ in x], axis=1), use_container_width=True)
                    
                    st.caption("ℹ️ टीप: वेळेची मर्यादा ६ मिनिटे आहे. हिरवा रंग = वेळेत पूर्ण, लाल रंग = वेळ संपल्यानंतर.")
                else:
                    st.info("अजून एकही परीक्षा दिलेली नाही.")
            except:
                st.warning("निकालाचा डेटा ('exam_results' शीट) सापडला नाही.")

            # --- हजेरी विभाग ---
            st.divider()
            st.subheader("📅 माझी हजेरी")
            try:
                att_sheet = workbook.worksheet("attendance_logs")
                att_data = pd.DataFrame(att_sheet.get_all_records())
                my_att = att_data[att_data['student_id'].astype(str) == str(current_sid)].copy()
                if not my_att.empty:
                    st.dataframe(my_att[['date', 'status', 'class_type']], use_container_width=True)
            except: st.write("हजेरी उपलब्ध नाही.")

            # --- फी विभाग ---
            st.divider()
            st.subheader("💰 फी तपशील")
            f1, f2, f3 = st.columns(3)
            t_val = safe_int(info.get('total_fees'), 6000)
            p_val = safe_int(info.get('paid_fees'), 0)
            f1.metric("एकूण फी", f"₹{t_val}")
            f2.metric("भरलेली फी", f"₹{p_val}")
            f3.metric("बाकी", f"₹{t_val - p_val}")
            
            if st.sidebar.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

    # --- ADMIN PANEL विभाग ---
    elif choice == "Admin Panel":
        st.header("🛠️ Admin Control Center")
        admin_pwd = st.sidebar.text_input("Admin Password", type="password")
        
        if admin_pwd == "VISHWA_ADMIN_123":
            t1, t2, t3, t4, t5, t6 = st.tabs(["➕ विद्यार्थी", "📝 हजेरी", "📊 यादी", "🔄 फी", "💰 रिपोर्ट", "🏆 मार्क भरा"])
            
            with t6:
                st.subheader("🏆 विद्यार्थ्यांचे परीक्षेचे मार्क भरा")
                with st.form("exam_score_form"):
                    e_sid = st.selectbox("विद्यार्थी निवडा", df['student_id'].tolist() if not df.empty else [])
                    e_id = st.text_input("पेपर क्रमांक (Paper No.)", value="Unit Test 1")
                    e_att = st.number_input("Attempted Questions", min_value=0)
                    e_corr = st.number_input("Correct Answers", min_value=0)
                    e_score = st.number_input("Final Score (Out of 100)", min_value=0, max_value=100)
                    e_time = st.number_input("घेतलेला वेळ (मिनिटात) - उदा. 5.5", min_value=0.0, step=0.1)
                    
                    if st.form_submit_button("निकाल सेव्ह करा"):
                        try:
                            ex_sheet = workbook.worksheet("exam_results")
                            ex_sheet.append_row([e_sid, e_id, e_att, e_corr, e_score, e_time, str(datetime.now().date())])
                            st.success("✅ निकाल अपडेट झाला!")
                        except:
                            st.error("'exam_results' नावाची शीट गुगल शीटमध्ये तयार करा!")

            # (बाकीचे टॅब्स आधीसारखेच राहतील...)
            with t1: st.write("नवीन नोंदणी विभाग") # इथून पुढचा आधीचा कोड कंटिन्यू होतो...
