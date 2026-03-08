import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd

# कनेक्शन प्रस्थापित करणे
conn = st.connection("gsheets", type=GSheetsConnection)

# --- Admin Panel मधील 'Save' लॉजिक ---
def update_student_data(new_df):
    conn.update(worksheet="Sheet1", data=new_df)
    st.success("डेटा यशस्वीरित्या अपडेट झाला!")

# Admin Panel मध्ये Attendance मार्क करण्यासाठी:
def mark_attendance(sid, status, date):
    # 'attendance_logs' शीटमध्ये डेटा लिहिणे
    log_data = pd.DataFrame([[sid, date, status]], columns=['student_id', 'date', 'status'])
    # जुना डेटा वाचून त्यात हा नवीन डेटा जोडणे
    existing_logs = conn.read(worksheet="attendance_logs")
    updated_logs = pd.concat([existing_logs, log_data], ignore_index=True)
    conn.update(worksheet="attendance_logs", data=updated_logs)
    st.success(f"{sid} साठी हजेरी लागली!")
