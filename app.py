import streamlit as st
from st_gsheets_connection import GSheetsConnection

# पेज सेटअप
st.set_page_config(page_title="Vishwajeet Classes Portal")

# १. Google Sheet शी कनेक्शन जोडणे
# 'spreadsheet' मध्ये तुमच्या शीटची पूर्ण लिंक टाका
url = "तुमच्या_गूगल_शीटची_लिंक_येथे_टाका"
conn = st.connection("gsheets", type=GSheetsConnection)

def main():
    # शीटमधील डेटा वाचणे
    try:
        df = conn.read(spreadsheet=url)
        # डेटा डिक्शनरीमध्ये रूपांतरित करणे (Login साठी सोपे पडते)
        # तुमच्या शीटमध्ये 'student_id' हा कॉलम असावा
        data = df.set_index('student_id').to_dict('index')
    except:
        st.error("शीट कनेक्ट होऊ शकली नाही. लिंक चेक करा!")
        return

    st.sidebar.title("🔐 विद्यार्थी लॉगिन")
    sid = st.sidebar.text_input("विद्यार्थी ID")
    pwd = st.sidebar.text_input("पासवर्ड", type="password")
    
    if st.sidebar.button("Login"):
        # पासवर्ड चेक करणे (शीटमधील 'password' कॉलमशी)
        if sid in data and str(data[sid]["password"]) == pwd:
            st.session_state["logged_in"] = True
            st.session_state["student_info"] = data[sid]
            st.session_state["student_name"] = data[sid]["name"]
        else:
            st.sidebar.error("ID किंवा पासवर्ड चुकीचा आहे!")

    # लॉगिन झाल्यावर काय दिसेल
    if st.session_state.get("logged_in"):
        info = st.session_state["student_info"]
        st.title(f"🚩 स्वागत आहे, {st.session_state['student_name']}!")
        
        # शीटमधील इतर माहिती दाखवणे
        col1, col2, col3 = st.columns(3)
        col1.metric("लेव्हल", info['level'])
        col2.metric("हजेरी", f"{info['attendance']}%")
        col3.write(f"**फी स्टेटस:** {info['fees']}")
        
        st.info(f"**गुरुजींचा संदेश:** {info['progress_remark']}")
        
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    else:
        st.title("विश्वजीत क्लासेस - अधिकृत पोर्टल")
        st.write("कृपया तुमच्या वैयक्तिक प्रगतीसाठी डावीकडून लॉगिन करा.")

if __name__ == "__main__":
    main()
