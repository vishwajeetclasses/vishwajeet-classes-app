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
            
            st.title(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            
            col_img, col_info = st.columns([1, 3])
            with col_img:
                photo_url = info.get('photo_url', "")
                try:
                    if photo_url: st.image(photo_url, width=150)
                    else: st.image("https://via.placeholder.com/150", width=150)
                except: st.image("https://via.placeholder.com/150", width=150)
            
            with col_info:
                st.subheader("📊 माझी प्रगती")
                c1, c2 = st.columns(2)
                c1.metric("Abacus Level", info.get('abacus_level', 'N/A'))
                c2.metric("Vedic Math", info.get('vedic_level', 'N/A'))

            # --- परीक्षा निकाल विभाग ---
            st.divider()
            st.subheader("📝 माझे परीक्षेचे निकाल")
            try:
                exam_sheet = workbook.worksheet("exam_results")
                exam_df = pd.DataFrame(exam_sheet.get_all_records())
                my_exams = exam_df[exam_df['student_id'].astype(str) == str(current_sid)].copy()
                
                if not my_exams.empty:
                    # Accuracy Calculation
                    my_exams['Accuracy'] = (my_exams['correct_ans'] / my_exams['attempted'] * 100).round(1).astype(str) + '%'
                    
                    # Display Table with Style
                    def highlight_time(row):
                        return ['color: green' if float(row.time_taken) <= 6.0 else 'color: red'] * len(row)
                    
                    st.table(my_exams[['exam_id', 'attempted', 'correct_ans', 'score', 'time_taken', 'Accuracy']])
                    st.info("💡 टीप: ६ मिनिटांच्या आत पेपर सोडवणे अनिवार्य आहे.")
                else:
                    st.write("अद्याप कोणताही निकाल उपलब्ध नाही.")
            except:
                st.warning("निकालाचा डेटा उपलब्ध नाही (exam_results शीट तपासा).")

            # --- हजेरी विभाग ---
            st.divider()
            st.subheader("📅 माझी हजेरी")
            try:
                att_sheet = workbook.worksheet("attendance_logs")
                att_data = pd.DataFrame(att_sheet.get_all_records())
                my_att = att_data[att_data['student_id'].astype(str) == str(current_sid)].copy()
                if not my_att.empty:
                    st.dataframe(my_att[['date', 'status', 'class_type']], use_container_width=True)
            except: st.write("हजेरीची नोंद नाही.")

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
            tabs = st.tabs(["➕ विद्यार्थी", "📝 हजेरी", "📊 यादी", "🔄 फी", "💰 रिपोर्ट", "🏆 मार्क भरा"])
            
            with tabs[0]:
                st.subheader("नवीन नोंदणी")
                with st.form("add_student"):
                    n_sid = st.text_input("विद्यार्थी ID")
                    n_name = st.text_input("नाव")
                    if st.form_submit_button("सेव्ह करा"):
                        sheet1.append_row([n_sid, "12345", n_name, "", "", "None", "None", "0", 6000, 0, 6000, "नवीन"])
                        st.success("विद्यार्थी जोडला!"); st.rerun()

            with tabs[1]:
                st.subheader("हजेरी भरा")
                att_date = st.date_input("तारीख", datetime.now())
                att_records = []
                for idx, row in df.iterrows():
                    pres = st.checkbox(f"{row['name']} ({row['student_id']})", key=f"at_{row['student_id']}")
                    att_records.append([row['student_id'], str(att_date), "Present" if pres else "Absent", "General"])
                if st.button("हजेरी सेव्ह करा"):
                    workbook.worksheet("attendance_logs").append_rows(att_records)
                    st.success("हजेरी यशस्वी!")

            with tabs[2]:
                st.dataframe(df)

            with tabs[3]:
                st.subheader("फी अपडेट")
                s_name = st.selectbox("विद्यार्थी", df['name'].tolist() if not df.empty else [])
                u_total = st.number_input("एकूण फी", value=6000)
                u_paid = st.number_input("भरलेली फी", value=0)
                if st.button("अपडेट करा"):
                    cell = sheet1.find(s_name)
                    sheet1.update_cell(cell.row, 9, u_total)
                    sheet1.update_cell(cell.row, 10, u_paid)
                    st.success("अपडेट झाले!"); st.rerun()

            with tabs[4]:
                st.write("फी रिपोर्ट लवकरच उपलब्ध होईल.")

            with tabs[5]:
                st.subheader("🏆 मार्क भरा")
                with st.form("exam_form"):
                    e_sid = st.selectbox("ID", df['student_id'].tolist() if not df.empty else [])
                    e_id = st.text_input("पेपर नं.", value="Test 1")
                    e_att = st.number_input("Attempted", value=0)
                    e_corr = st.number_input("Correct", value=0)
                    e_score = st.number_input("Score", value=0)
                    e_time = st.number_input("Time (Min)", value=0.0, step=0.1)
                    if st.form_submit_button("निकाल सेव्ह करा"):
                        workbook.worksheet("exam_results").append_row([e_sid, e_id, e_att, e_corr, e_score, e_time, str(datetime.now().date())])
                        st.success("निकाल सेव्ह झाला!")

        elif admin_pwd: st.error("चुकीचा पासवर्ड!")

if __name__ == "__main__":
    main()
