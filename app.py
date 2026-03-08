import streamlit as st
import pandas as pd

# १. पेज सेटअप - एकदम साधे आणि स्वच्छ
st.set_page_config(page_title="Vishwajeet Classes", layout="centered")

# २. गुगल शीट कनेक्शन
def load_data():
    # तुमची शीटची लिंक येथे पेस्ट करा
    sheet_url = "https://docs.google.com/spreadsheets/d/1IMw_nRER8fz-yUtgwKyt12Xmw4ZgwoSh4a19seAFzqc/edit?usp=sharing"
    
    if "edit" in sheet_url:
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
    else:
        csv_url = sheet_url
    try:
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return None

def main():
    df = load_data()
    
    if df is not None:
        data_dict = df.set_index('student_id').to_dict('index')

        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False

        if not st.session_state["logged_in"]:
            # लॉगिन विभाग
            st.header("🚩 विश्वजीत क्लासेस")
            st.subheader("विद्यार्थी लॉगिन पोर्टल")
            
            # साधी लॉगिन सिस्टिम (कोणतेही CSS नाही)
            sid = st.text_input("विद्यार्थी ID (Student ID)")
            pwd = st.text_input("पासवर्ड", type="password")
            
            if st.button("लॉगिन करा"):
                if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                    st.session_state["logged_in"] = True
                    st.session_state["info"] = data_dict[sid]
                    st.rerun()
                else:
                    st.error("ID किंवा पासवर्ड चुकीचा आहे!")
        else:
            # लॉगिन नंतरचा डॅशबोर्ड
            info = st.session_state["info"]
            
            st.title(f"नमस्ते, {info.get('name', 'विद्यार्थी')}! 👋")
            
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()

            st.write("---")

            # माहिती दाखवण्यासाठी साधे कॉलम्स
            col1, col2 = st.columns(2)
            col1.info(f"**लेव्हल:**\n\n{info.get('level', 'N/A')}")
            col2.success(f"**हजेरी:**\n\n{info.get('attendance', '0')}%")

            fee = str(info.get('fees', 'Pending')).capitalize()
            st.warning(f"**फी स्टेटस:** {fee}")

            st.write("---")
            st.write("### 📝 गुरुजींचा अभिप्राय:")
            st.write(info.get('progress_remark', 'उत्तम प्रगती!'))

    else:
        st.error("डेटा लोड झाला नाही. कृपया इंटरनेट कनेक्शन तपासा.")

if __name__ == "__main__":
    main()


