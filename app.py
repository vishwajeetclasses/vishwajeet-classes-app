import streamlit as st
import pandas as pd

# १. पेज सेटअप (App Look)
st.set_page_config(
    page_title="Vishwajeet Classes", 
    page_icon="🎓", 
    layout="centered"
)

# २. गुगल शीट कनेक्शन (Data Loading)
def load_data():
    # तुमची शीटची लिंक येथे पेस्ट करा
    sheet_url = "तुमची_पूर्ण_शीट_लिंक_येथे_टाका"
    
    if "edit" in sheet_url:
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
    else:
        csv_url = sheet_url
    try:
        # ऑनलाईन डेटा वाचणे
        df = pd.read_csv(csv_url)
        # कॉलमची नावे क्लिन करणे
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def main():
    df = load_data()
    
    if df is not None:
        # डिक्शनरी तयार करणे
        data_dict = df.set_index('student_id').to_dict('index')

        # लॉगिन स्थिती तपासणे
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            # --- लॉगिन स्क्रीन ---
            st.markdown("<h1 style='text-align: center; color: #007bff;'>🚩 विश्वजीत क्लासेस</h1>", unsafe_allow_html=True)
            st.write("---")
            
            # लॉगिन फॉर्म (यामध्ये बटण नक्की क्लिक होईल)
            with st.form("login_form"):
                sid = st.text_input("विद्यार्थी ID (Student ID)", placeholder="उदा. VC101")
                pwd = st.text_input("पासवर्ड", type="password")
                submit = st.form_submit_button("लॉगिन करा")
                
                if submit:
                    if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["info"] = data_dict[sid]
                        st.rerun()
                    else:
                        st.error("ID किंवा पासवर्ड चुकीचा आहे!")
            
            st.info("सूचना: लॉगिन करण्यासाठी तुमचा आयडी आणि पासवर्ड वापरा.")

        else:
            # --- डॅशबोर्ड (लॉगिन नंतर) ---
            info = st.session_state["info"]
            
            # टॉप बार (स्वागत आणि लॉगआउट)
            col_top1, col_top2 = st.columns([0.7, 0.3])
            with col_top1:
                st.subheader(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            with col_top2:
                if st.button("Logout"):
                    st.session_state["logged_in"] = False
                    st.rerun()

            st.write("---")

            # प्रगती कार्ड्स (Simple & Functional)
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"**लेव्हल:** \n## {info.get('level', 'N/A')}")
            with c2:
                st.success(f"**हजेरी:** \n## {info.get('attendance', '0')}%")

            # फी स्टेटस
            fee = str(info.get('fees', 'Pending')).capitalize()
            if fee == "Paid":
                st.balloons() # फी भरलेली असेल तर सेलिब्रेशन
                st.write("✅ **फी स्टेटस:** पूर्ण भरली आहे.")
            else:
                st.warning("⚠️ **फी स्टेटस:** प्रलंबित (Pending)")

            st.write("---")
            
            # रिमार्क सेक्शन
            st.write("### 📝 गुरुजींचा अभिप्राय:")
            st.markdown(f"> {info.get('progress_remark', 'उत्तम प्रगती!')}")

            # क्लास अपडेट्स
            with st.expander("📢 महत्वाच्या सूचना"):
                st.write("१. पुढील आठवड्यात अ‍ॅबॅकसची सराव परीक्षा होईल.")
                st.write("२. नवीन बॅच प्रवेश सुरू आहेत.")

    else:
        st.error("डेटा लोड होऊ शकला नाही. कृपया इंटरनेट आणि Google Sheet लिंक तपासा.")

if __name__ == "__main__":
    main()
