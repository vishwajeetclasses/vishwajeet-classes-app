import streamlit as st
import pandas as pd

# १. पेज कॉन्फिगरेशन (Mobile App Look)
st.set_page_config(
    page_title="Vishwajeet Classes", 
    page_icon="🎓", 
    layout="centered", # याने मजकूर मध्यभागी राहून ॲपसारखा दिसेल
    initial_sidebar_state="collapsed"
)

# CSS फॉर 'App Look' (बॅकग्राउंड कलर आणि कार्ड डिझाइन)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# २. गुगल शीट कनेक्शन
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc/edit?usp=sharingा"
    if "edit" in sheet_url:
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
    else:
        csv_url = sheet_url
    try:
        return pd.read_csv(csv_url)
    except:
        return None

def main():
    df = load_data()
    
    if df is not None:
        # कॉलमची नावे व्यवस्थित करणे (Spaces काढणे)
        df.columns = [c.strip().lower() for c in df.columns]
        data_dict = df.set_index('student_id').to_dict('index')

        # लॉगिन स्टेटस चेक
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            # लॉगिन स्क्रीन
            st.markdown("<h2 style='text-align: center;'>🚩 विश्वजीत क्लासेस</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center;'>विद्यार्थी लॉगिन पोर्टल</p>", unsafe_allow_html=True)
            
            with st.container():
                sid = st.text_input("विद्यार्थी ID", placeholder="उदा. VC101")
                pwd = st.text_input("पासवर्ड", type="password", placeholder="••••••••")
                
                if st.button("लॉगिन करा"):
                    if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[sid]
                        st.rerun()
                    else:
                        st.error("ID किंवा पासवर्ड चुकीचा आहे!")
            
            st.markdown("---")
            st.info("💡 पासवर्ड विसरला असल्यास क्लासमध्ये संपर्क साधा.")
        
        else:
            # डॅशबोर्ड (लॉगिन नंतर)
            info = st.session_state["info"]
            
            # टॉप बार
            cols = st.columns([0.8, 0.2])
            cols[0].markdown(f"### नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            if cols[1].button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

            st.markdown("---")

            # प्रगती कार्ड्स (Row 1)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='metric-card'><b>लेव्हल:</b><br><span style='font-size:24px; color:#007bff;'>{info.get('level', 'N/A')}</span></div>", unsafe_allow_html=True)
            with c2:
                # 'attendance' कॉलम नाव नीट तपासा
                att = info.get('attendance', '0')
                st.markdown(f"<div class='metric-card'><b>हजेरी:</b><br><span style='font-size:24px; color:#28a745;'>{att}%</span></div>", unsafe_allow_html=True)

            # फी स्टेटस (Row 2)
            fee_status = str(info.get('fees', 'Pending')).capitalize()
            color = "#28a745" if fee_status == "Paid" else "#dc3545"
            st.markdown(f"<div class='metric-card'><b>फी स्टेटस:</b> <span style='color:{color}; font-weight:bold;'>{fee_status}</span></div>", unsafe_allow_html=True)

            # रिमार्क
            st.markdown("#### 📝 गुरुजींचा अभिप्राय:")
            st.success(info.get('progress_remark', 'तुमची प्रगती चांगली आहे!'))

            # एक्स्ट्रा फीचर्स (Public/Updates)
            with st.expander("📢 क्लास अपडेट्स (नवीन बॅच/सुट्ट्या)"):
                st.write("* नवीन अ‍ॅबॅकस बॅच १० मार्चपासून सुरू होत आहे.")
                st.write("* या रविवारी क्लासला सुट्टी असेल.")

    else:
        st.error("डेटाबेस कनेक्ट होऊ शकला नाही. कृपया Google Sheet लिंक तपासा.")

if __name__ == "__main__":
    main()

