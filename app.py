import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# डेटा लोड करणे
def load_data(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return None

def main():
    # तुमची गुगल शीट लिंक येथे टाका
    sheet_url = "https://docs.google.com/spreadsheets/d/1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc/edit?usp=sharingा"
    df = load_data(sheet_url)

    if df is not None:
        data_dict = df.set_index('student_id').to_dict('index')

        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            st.title("🚩 विश्वजीत क्लासेस")
            sid = st.text_input("विद्यार्थी ID")
            pwd = st.text_input("पासवर्ड", type="password")
            if st.button("Login"):
                if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["sid"] = sid
                    st.session_state["info"] = data_dict[sid]
                    st.rerun()
                else:
                    st.error("ID/Password चुकीचा आहे!")
        else:
            # --- STUDENT DASHBOARD ---
            info = st.session_state["info"]
            
            with st.sidebar:
                st.image(info.get('photo_url', "https://via.placeholder.com/150"), width=100)
                st.write(f"**{info.get('name')}**")
                if st.button("Logout"):
                    st.session_state["logged_in"] = False
                    st.rerun()

            # Profile Info
            st.title(f"विद्यार्थी डॅशबोर्ड - {info.get('name')}")
            
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Abacus:** {info.get('abacus_level')}")
            c2.success(f"**Vedic Math:** {info.get('vedic_level')}")
            c3.warning(f"**Fees:** {info.get('fees')}")

            st.divider()

            # --- CALENDAR VIEW LOGIC ---
            st.subheader("📅 हजेरी कॅलेंडर (Attendance)")
            st.markdown("""
            <style>
            .present { background-color: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center; }
            .absent { background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; text-align: center; }
            .holiday { background-color: #ffc107; color: black; padding: 10px; border-radius: 5px; text-align: center; }
            .emergency { background-color: #007bff; color: white; padding: 10px; border-radius: 5px; text-align: center; }
            </style>
            """, unsafe_allow_html=True)

            # एक साधी कॅलेंडर ग्रीड (Sample)
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            cols = st.columns(7)
            for i, day in enumerate(days):
                cols[i].write(f"**{day}**")
            
            # येथे आपण डेटाबेसवरून रंग ठरवू शकतो, सध्या सॅम्पल म्हणून:
            c = st.columns(7)
            c[0].markdown('<div class="present">1</div>', unsafe_allow_html=True)
            c[1].markdown('<div class="absent">2</div>', unsafe_allow_html=True)
            c[2].markdown('<div class="holiday">3</div>', unsafe_allow_html=True)
            c[3].markdown('<div class="present">4</div>', unsafe_allow_html=True)
            c[4].markdown('<div class="emergency">5</div>', unsafe_allow_html=True)
            c[5].markdown('<div class="present">6</div>', unsafe_allow_html=True)
            c[6].markdown('<div class="present">7</div>', unsafe_allow_html=True)

    else:
        st.error("डेटाबेस कनेक्ट झाला नाही.")

if __name__ == "__main__":
    main()
