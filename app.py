import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# १. पेज सेटअप
st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# --- CUSTOM CSS (Branding आणि Header पूर्णपणे काढण्यासाठी) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            #stDecoration {display:none !important;}
            [data-testid="stHeader"] {display:none !important;}
            /* मोबाईलवर वरची रिकामी जागा काढण्यासाठी */
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# डेटा सुरक्षितपणे नंबरमध्ये बदलण्यासाठी फंक्शन
def safe_int(val, default=0):
    try:
        if val == '' or val is None: 
            return default
        return int(float(str(val).replace(',', '')))
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
    # डेटा लोड करणे
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
        if "logged_in" not in st.session_state: st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            if 'student_id' in df.columns:
                # लॉगिनसाठी सोपे मॅपिंग
                data_dict = df.set_index(df['student_id'].astype(str)).to_dict('index')
                sid = st.text_input("विद्यार्थी ID")
                pwd = st.text_input("पासवर्ड", type="password")
                if st.button("लॉगिन"):
                    if str(sid) in data_dict and str(data_dict[str(sid)].get("password")) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[str(sid)]
                        st.session_state["sid"] = sid
                        st.rerun()
                    else: st.error("चुकीचा ID किंवा पासवर्ड!")
        else:
            info = st.session_state.get("info", {})
            current_sid = st.session_state.get("sid", "")
            
            st.title(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            
            col_img, col_info = st.columns([1, 3])
            with col_img:
                photo_url = info.get('photo_url', "")
                try:
                    if photo_url: st.image(photo_url, width=150)
                    else: st.image("https://via.placeholder.com/150", caption="No Photo", width=150)
                except: st.image("https://via.placeholder.com/150", width=150)
            
            with col_info:
                st.subheader("📝 वैयक्तिक माहिती")
                st.write(f"**पत्ता:** {info.get('address', 'N/A')}")
                c1, c2 = st.columns(2)
                c1.metric("Abacus Level", info.get('abacus_level', 'N/A'))
                c2.metric("Vedic Math", info.get('vedic_level', 'N/A'))

            # --- परीक्षा निकाल विभाग ---
            st.divider()
            st.subheader("🏆 माझे परीक्षेचे निकाल")
            try:
                exam_sheet = workbook.worksheet("exam_results")
                exam_df = pd.DataFrame(exam_sheet.get_all_records())
                my_exams = exam_df[exam_df['student_id'].astype(str) == str(current_sid)].copy()
                
                if not my_exams.empty:
                    my_exams['Accuracy'] = (my_exams['correct_ans'] / my_exams['attempted'] * 100).round(1).astype(str) + '%'
                    
                    def style_time(val):
                        color = 'green' if float(val) <= 6.0 else 'red'
                        return f'color: {color}; font-weight: bold'

                    st.dataframe(my_exams[['exam_id', 'attempted', 'correct_ans', 'score', 'time_taken', 'Accuracy']].style.applymap(style_time, subset=['time_taken']), use_container_width=True)
                else: st.info("अद्याप कोणताही निकाल उपलब्ध नाही.")
            except: st.warning("निकालाचा डेटा सापडला नाही.")

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
            with st.container(border=True):
                f1, f2, f3 = st.columns(3)
                t_val = safe_int(info.get('total_fees'), 0)
                p_val = safe_int(info.get('paid_fees'), 0)
                r_val = t_val - p_val
                f1.metric("एकूण फी", f"₹{t_val}")
                f2.metric("भरलेली फी", f"₹{p_val}")
                f3.metric("बाकी फी", f"₹{r_val}", delta=f"-₹{r_val}" if r_val > 0 else "Clear", delta_color="inverse")

            if st.sidebar.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

    # --- ADMIN PANEL विभाग ---
    elif choice == "Admin Panel":
        st.header("🛠️ Admin Control Center")
        admin_pwd = st.sidebar.text_input("Admin Password", type="password")
        
        if admin_pwd == "VISHWA_ADMIN_123":
            tabs = st.tabs(["➕ नवीन विद्यार्थी", "📝 हजेरी भरा", "📊 विद्यार्थी यादी", "🔄 फी अपडेट", "💰 फी रिपोर्ट", "🏆 मार्क भरा"])
            
            with tabs[0]:
                st.subheader("नवीन नोंदणी")
                with st.form("add_student_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    n_sid = c1.text_input("विद्यार्थी ID")
                    n_name = c2.text_input("पूर्ण नाव")
                    n_pwd = c1.text_input("पासवर्ड", value="12345")
                    n_photo = c2.text_input("फोटो URL")
                    n_addr = st.text_area("पत्ता")
                    n_abacus = c1.selectbox("Abacus Level", ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "None"])
                    n_vedic = c2.selectbox("Vedic Math", ["Level 1", "Level 2", "Level 3", "None"])
                    n_total = c1.number_input("एकूण फी", value=6000)
                    n_paid = c2.number_input("भरलेली फी", value=0)
                    if st.form_submit_button("विद्यार्थी सेव्ह करा"):
                        if n_sid and n_name:
                            sheet1.append_row([n_sid, n_pwd, n_name, n_photo, n_addr, n_abacus, n_vedic, "0", n_total, n_paid, n_total-n_paid, "नवीन"])
                            st.success(f"✅ {n_name} ची नोंदणी यशस्वी! डेटा रिफ्रेश होत आहे...")
                            st.rerun()

            with tabs[1]:
                st.subheader("क्लास हजेरी")
                att_date = st.date_input("तारीख", datetime.now())
                col_a, col_v = st.columns(2)
                att_list = []
                with col_a:
                    st.write("🧮 Abacus Class")
                    ab_df = df[df['abacus_level']!='None']
                    for i, r in ab_df.iterrows():
                        p = st.checkbox(f"{r['name']}", key=f"ab_{r['student_id']}")
                        att_list.append([r['student_id'], str(att_date), "Present" if p else "Absent", "Abacus"])
                with col_v:
                    st.write("🕉️ Vedic Math")
                    vd_df = df[df['vedic_level']!='None']
                    for i, r in vd_df.iterrows():
                        p = st.checkbox(f"{r['name']}", key=f"vd_{r['student_id']}")
                        att_list.append([r['student_id'], str(att_date), "Present" if p else "Absent", "Vedic"])
                
                if st.button("हजेरी सेव्ह करा"):
                    if att_list:
                        workbook.worksheet("attendance_logs").append_rows(att_list)
                        st.success("✅ हजेरी यशस्वीरित्या सेव्ह झाली!")
                    else: st.warning("विद्यार्थी यादी रिकामी आहे.")

            with tabs[2]:
                st.subheader("सर्व विद्यार्थी माहिती")
                st.dataframe(df, use_container_width=True)

            with tabs[3]:
                st.subheader("फी अपडेट")
                if not df.empty:
                    s_update = st.selectbox("विद्यार्थी निवडा", df['name'].tolist())
                    u_row = df[df['name'] == s_update].iloc[0]
                    new_t = st.number_input("Total Fees", value=safe_int(u_row['total_fees']))
                    new_p = st.number_input("Paid Fees", value=safe_int(u_row['paid_fees']))
                    if st.button("फी अपडेट करा"):
                        cell = sheet1.find(str(u_row['student_id']))
                        sheet1.update_cell(cell.row, 9, new_t)
                        sheet1.update_cell(cell.row, 10, new_p)
                        sheet1.update_cell(cell.row, 11, new_t-new_p)
                        st.success("✅ फी अपडेट झाली!")
                        st.rerun()

            with tabs[4]:
                st.subheader("💰 फी रिपोर्ट (Live Update)")
                if not df.empty:
                    report_df = df.copy()
                    report_df['total_fees'] = report_df['total_fees'].apply(safe_int)
                    report_df['paid_fees'] = report_df['paid_fees'].apply(safe_int)
                    report_df['remaining'] = report_df['total_fees'] - report_df['paid_fees']
                    
                    t_f = report_df['total_fees'].sum()
                    p_f = report_df['paid_fees'].sum()
                    rem_f = report_df['remaining'].sum()
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("एकूण अपेक्षित फी", f"₹{t_f}")
                    m2.metric("ज जमा झालेली फी", f"₹{p_f}")
                    m3.metric("एकूण बाकी फी", f"₹{rem_f}", delta=f"-₹{rem_f}", delta_color="inverse")
                    
                    st.divider()
                    st.write("### 📝 विद्यार्थ्यांनुसार थकबाकी यादी")
                    display_report = report_df[['student_id', 'name', 'total_fees', 'paid_fees', 'remaining']].copy()
                    display_report.columns = ['ID', 'नाव', 'एकूण फी', 'भरलेली', 'बाकी']
                    st.dataframe(display_report.sort_values(by='बाकी', ascending=False), use_container_width=True)

            with tabs[5]:
                st.subheader("🏆 परीक्षेचे मार्क भरा")
                with st.form("mark_form", clear_on_submit=True):
                    m_sid = st.selectbox("विद्यार्थी निवडा", df['student_id'].tolist() if not df.empty else [])
                    m_id = st.text_input("पेपर क्रमांक/नाव", value="Exam-1")
                    c1, c2, c3 = st.columns(3)
                    m_att = c1.number_input("Attempted", min_value=0)
                    m_corr = c2.number_input("Correct", min_value=0)
                    m_time = c3.number_input("वेळ (Min)", value=5.0, step=0.1)
                    m_score = st.number_input("स्कोर (/100)", min_value=0)
                    if st.form_submit_button("निकाल सेव्ह करा"):
                        try:
                            workbook.worksheet("exam_results").append_row([m_sid, m_id, m_att, m_corr, m_score, m_time, str(datetime.now().date())])
                            st.success("✅ निकाल सेव्ह झाला!")
                        except: st.error("exam_results शीट तपासा!")

        elif admin_pwd: st.error("पासवर्ड चुकीचा आहे!")

if __name__ == "__main__":
    main()
