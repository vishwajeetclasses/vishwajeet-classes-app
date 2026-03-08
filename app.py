import streamlit as st
import pandas as pd
from datetime import datetime

# Connection लायब्ररी सुरक्षितपणे लोड करणे
try:
    from st_gsheets_connection import GSheetsConnection
except ModuleNotFoundError:
    st.error("अजून लायब्ररी लोड होत आहे... कृपया १-२ मिनिटांनी 'Reboot' करा.")
    st.stop()

# 1. Page Setup
st.set_page_config(page_title="Vishwajeet Classes Dashboard", layout="wide")

# Admin Password (tumcha avadta password ithe taka)
ADMIN_PASSWORD = "VISHWA_ADMIN_123"

# 2. Connection Setup (Secrets madhun automatically connect hoil)
conn = st.connection("gsheets", type=GSheetsConnection)

# Data Load karnyache function
def get_all_data():
    return conn.read(worksheet="Sheet1", ttl="0s") # ttl=0 mhanje nehami fresh data yeil

def get_attendance_logs():
    return conn.read(worksheet="attendance_logs", ttl="0s")

def main():
    df = get_all_data()
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Sidebar Navigation
    st.sidebar.title("🚩 Vishwajeet Classes")
    choice = st.sidebar.selectbox("Vibhag Nivada", ["Student Login", "Admin Panel"])

    if choice == "Student Login":
        st.header("🎓 Student Portal")
        data_dict = df.set_index('student_id').to_dict('index')
        
        if "student_logged_in" not in st.session_state:
            st.session_state["student_logged_in"] = False

        if not st.session_state["student_logged_in"]:
            sid = st.text_input("Vidyarthi ID")
            pwd = st.text_input("Password", type="password")
            if st.button("Login"):
                if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                    st.session_state["student_logged_in"] = True
                    st.session_state["student_info"] = data_dict[sid]
                    st.session_state["current_sid"] = sid
                    st.rerun()
                else:
                    st.error("ID kiwa Password chukicha ahe!")
        else:
            # --- Student Dashboard View ---
            info = st.session_state["student_info"]
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.image(info.get('photo_url', "https://via.placeholder.com/150"), width=150)
            with col2:
                st.title(f"Namaste, {info.get('name')}!")
                st.write(f"📍 **Address:** {info.get('address', 'N/A')}")
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Abacus Level", info.get('abacus_level', 'N/A'))
            c2.metric("Vedic Math", info.get('vedic_level', 'N/A'))
            
            fee_status = str(info.get('fees')).capitalize()
            color = "green" if fee_status == "Paid" else "red"
            c3.markdown(f"**Fee Status:** :{color}[{fee_status}]")

            st.write("---")
            st.subheader("📅 Attendance Highlights")
            st.info(f"Hajeri: {info.get('attendance_percent', 0)}% | Remark: {info.get('progress_remark', 'Pragati changli ahe.')}")

            if st.sidebar.button("Logout"):
                st.session_state["student_logged_in"] = False
                st.rerun()

    elif choice == "Admin Panel":
        st.header("🛠️ Admin Control Center")
        admin_pwd = st.sidebar.text_input("Admin Password", type="password")

        if admin_pwd == ADMIN_PASSWORD:
            tab1, tab2, tab3 = st.tabs(["Student Management", "Attendance Entry", "Fee Tracker"])

            with tab1:
                st.subheader("Vidyarthi Mahiti Update Kara")
                selected_name = st.selectbox("Vidyarthi Nivada", df['name'].tolist())
                student_row = df[df['name'] == selected_name].iloc[0]
                
                with st.form("edit_form"):
                    new_name = st.text_input("Full Name", value=student_row['name'])
                    new_photo = st.text_input("Photo URL", value=student_row['photo_url'])
                    new_addr = st.text_input("Address", value=student_row['address'])
                    new_abacus = st.text_input("Abacus Level", value=student_row['abacus_level'])
                    new_vedic = st.text_input("Vedic Level", value=student_row['vedic_level'])
                    new_remark = st.text_area("Progress Remark", value=student_row['progress_remark'])
                    
                    if st.form_submit_button("Sheet Madhe Update Kara"):
                        # Dataframe madhe badal karne
                        df.loc[df['name'] == selected_name, ['name', 'photo_url', 'address', 'abacus_level', 'vedic_level', 'progress_remark']] = [new_name, new_photo, new_addr, new_abacus, new_vedic, new_remark]
                        conn.update(worksheet="Sheet1", data=df)
                        st.success("Data update jala!")

            with tab2:
                st.subheader("Dainandin Hajeri (Attendance)")
                target_sid = st.selectbox("Vidyarthi ID निवडा", df['student_id'].tolist())
                today = st.date_input("Tarikh", datetime.now())
                status = st.radio("Status", ["Present", "Absent", "Holiday", "Emergency"])
                
                if st.button("Hajeri Save Kara"):
                    logs = get_attendance_logs()
                    new_log = pd.DataFrame([[target_sid, str(today), status]], columns=['student_id', 'date', 'status'])
                    updated_logs = pd.concat([logs, new_log], ignore_index=True)
                    conn.update(worksheet="attendance_logs", data=updated_logs)
                    st.success(f"{target_sid} sathi {status} mark jale!")

            with tab3:
                st.subheader("Fee Management")
                st.dataframe(df[['student_id', 'name', 'fees', 'abacus_level']])
                st.write("Tip: Fee status badlanyasathi 'Student Management' tab vapra.")

        elif admin_pwd != "":
            st.error("Admin password chukicha ahe!")

if __name__ == "__main__":
    main()

