import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Setup
st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# Admin Password (yehe badla)
ADMIN_PASSWORD = "VISHWAJEET_ADMIN" 

# 2. Data Load Function
def load_data(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return None

def main():
    # Tumchi Google Sheet Link
    sheet_url = "https://docs.google.com/spreadsheets/d/1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc/edit?usp=sharing"
    df = load_data(sheet_url)

    if df is not None:
        data_dict = df.set_index('student_id').to_dict('index')

        # Sidebar Menu
        menu = st.sidebar.selectbox("Menu", ["Student Login", "Admin Panel"])

        if menu == "Student Login":
            if not st.session_state.get("logged_in"):
                st.title("🎓 Student Portal")
                sid = st.text_input("Vidyarthi ID")
                pwd = st.text_input("Password", type="password")
                if st.button("Login"):
                    if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[sid]
                        st.rerun()
                    else:
                        st.error("Chukicha ID/Password!")
            else:
                # --- STUDENT DASHBOARD ---
                info = st.session_state["info"]
                st.title(f"Namaste, {info['name']}!")
                
                # Profile Photo ani Basic Info
                col1, col2 = st.columns([0.2, 0.8])
                with col1:
                    st.image(info.get('photo_url', "https://via.placeholder.com/150"), width=120)
                with col2:
                    st.write(f"📍 **Address:** {info.get('address')}")
                    st.info(f"Abacus: {info.get('abacus_level')} | Vedic Math: {info.get('vedic_level')}")

                st.divider()
                
                # Attendance Calendar Look
                st.subheader("📅 Attendance")
                st.markdown("""
                <style>
                .box { padding:10px; border-radius:5px; text-align:center; font-weight:bold; color:white; }
                .p { background-color: #28a745; } .a { background-color: #dc3545; }
                .h { background-color: #ffc107; color:black; } .e { background-color: #007bff; }
                </style>
                """, unsafe_allow_html=True)
                
                st.write("Current Month Status:")
                c = st.columns(7)
                # Sample display - actual data 'attendance_logs' sheet madhun gheta yeil
                c[0].markdown('<div class="box p">1</div>', unsafe_allow_html=True)
                c[1].markdown('<div class="box a">2</div>', unsafe_allow_html=True)
                c[2].markdown('<div class="box h">3</div>', unsafe_allow_html=True)
                c[3].markdown('<div class="box p">4</div>', unsafe_allow_html=True)
                
                if st.button("Logout"):
                    st.session_state["logged_in"] = False
                    st.rerun()

        elif menu == "Admin Panel":
            st.title("🛠️ Admin Control Panel")
            admin_pwd = st.text_input("Admin Password Taka", type="password")
            
            if admin_pwd == ADMIN_PASSWORD:
                st.success("Access Granted!")
                
                tab1, tab2, tab3 = st.tabs(["Update Student", "Mark Attendance", "Fee Status"])
                
                with tab1:
                    st.write("### Student Information Update")
                    selected_student = st.selectbox("Vidyarthi Nivada", df['name'].tolist())
                    # Ithe tumi data edit karun update karu shakta
                    st.info("Update feature sathi Google Sheets API setup lagel.")

                with tab2:
                    st.write("### Hajeri Lavane")
                    date_input = st.date_input("Tarikh", datetime.now())
                    status = st.radio("Status", ["Present", "Absent", "Holiday", "Emergency"])
                    if st.button("Save Attendance"):
                        st.write(f"Data Saved for {date_input} as {status}")
                        # Logic to write to Google Sheet

                with tab3:
                    st.write("### Fee Management")
                    st.dataframe(df[['student_id', 'name', 'fees']])

            elif admin_pwd != "":
                st.error("Chukicha Admin Password!")

    else:
        st.error("Database connection failed!")

if __name__ == "__main__":
    main()
