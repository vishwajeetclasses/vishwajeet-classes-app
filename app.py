import streamlit as st
import pandas as pd
from datetime import datetime

# १. पेज सेटअप
st.set_page_config(page_title="Vishwajeet Classes Pro", layout="wide")

# २. डेटा लोड करणे
def load_data(url):
    try:
        csv_url = url.split('/edit')[0] + '/export?format=csv'
        return pd.read_csv(csv_url)
    except:
        return None

def main():
    # तुमची शीट लिंक (येथे टाका)
    sheet_url = "https://docs.google.com/spreadsheets/d/1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc/edit?usp=sharingा"
    df = load_data(sheet_url)

    if df is not None:
        df.columns = [c.strip().lower() for c in df.columns]
        data_dict = df.set_index('student_id').to_dict('index')

        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            # --- LOGIN SCREEN ---
            st.markdown("<h1 style='text-align: center;'>🎓 Vishwajeet Classes</h1>", unsafe_allow_html=True)
            with st.container():
                sid = st.text_input("विद्यार्थी ID")
                pwd = st.text_input("पासवर्ड", type="password")
                if st.button("लॉगिन करा"):
                    if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["sid"] = sid
                        st.session_state["info"] = data_dict[sid]
                        st.rerun()
                    else:
                        st.error("चुकीचा ID/Password!")
        else:
            # --- STUDENT DASHBOARD ---
            info = st.session_state["info"]
            
            # Sidebar Logout
            if st.sidebar.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

            # Profile Section
            col1, col2 = st.columns([0.3, 0.7])
            with col1:
                # फोटो नसेल तर प्लेसहोल्डर दाखवणे
                photo = info.get('photo_url', "https://www.w3schools.com/howto/img_avatar.png")
                st.image(photo, width=150, caption=f"ID: {st.session_state['sid']}")
            
            with col2:
                st.title(f"नमस्ते, {info.get('name')}!")
                st.write(f"📍 **पत्ता:** {info.get('address', 'N/A')}")

            st.divider()

            # Course & Progress
            c1, c2, c3 = st.columns(3)
            with c1:
                st.info(f"🧮 **Abacus Level**\n### {info.get('abacus_level', 'Basic')}")
            with c2:
                st.success(f"🔢 **Vedic Math**\n### {info.get('vedic_level', 'Basic')}")
            with c3:
                fee_status = str(info.get('fees')).capitalize()
                color = "green" if fee_status == "Paid" else "red"
                st.markdown(f"💰 **Fee Status**\n### :{color}[{fee_status}]")

            st.divider()

            # Attendance Calendar Feature
            st.subheader("📅 तुमची हजेरी (Attendance Calendar)")
            # येथे आपण एक साधा रंगीत मेसेज आणि चार्ट दाखवू शकतो
            st.write(f"एकूण हजेरी: **{info.get('attendance_percent', 0)}%**")
            
            # कॅलेंडर व्ह्यूसाठी 'Dummy' कलर कोडिंग (खऱ्या डेटासाठी आपण स्वतंत्र शीट जोडू)
            st.markdown("""
            🟢 **हिरवा:** उपस्थित | 🔴 **लाल:** अनुपस्थित | 🟡 **पिवळा:** सुट्टी | 🔵 **निळा:** इमर्जन्सी सुट्टी
            """)
            
            # येथे आपण प्रोग्रेस रिमार्क दाखवूया
            st.chat_message("teacher").write(f"**शिक्षकांचा अभिप्राय:** {info.get('progress_remark')}")

    else:
        st.error("डेटाबेस लोड होत नाहीये.")

if __name__ == "__main__":
    main()
