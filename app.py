import streamlit as st
import pandas as pd

# पेज कॉन्फिगरेशन
st.set_page_config(page_title="Vishwajeet Classes Portal", layout="wide")

# १. पब्लिक सेक्शन (सर्वांसाठी)
def public_home():
    st.title("🚩 विश्वजीत क्लासेस (Vishwajeet Classes)")
    st.subheader("अ‍ॅबॅकस आणि वैदिक गणित केंद्र")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://via.placeholder.com/400x200?text=Abacus+Class", caption="आमचा क्लास")
    with col2:
        st.write("""
        ### आमची वैशिष्ट्ये:
        * तज्ञ शिक्षक आणि वैयक्तिक लक्ष.
        * अ‍ॅबॅकसद्वारे गणिताची भीती घालवा.
        * वैदिक गणिताच्या सोप्या ट्रिक्स.
        * दरमहा प्रगती अहवाल.
        """)

# २. प्रायव्हेट सेक्शन (फक्त विद्यार्थ्यांसाठी - लॉगिन नंतर)
def student_dashboard(student_info):
    st.success(f"नमस्ते, {student_info['name']}! तुमच्या डॅशबोर्डवर स्वागत आहे.")
    
    # प्रगतीचे कार्ड्स
    m1, m2, m3 = st.columns(3)
    m1.metric("चालू लेव्हल", student_info['level'])
    m2.metric("हजेरी (Attendance)", f"{student_info['attendance']}%")
    
    fee_color = "green" if student_info['fees'] == "Paid" else "red"
    m3.markdown(f"**फी स्टेटस:** <span style='color:{fee_color}'>{student_info['fees']}</span>", unsafe_allow_status=True)

    st.divider()
    st.write("### 📝 शिक्षकांचा अभिप्राय (Teacher's Remark):")
    st.info(student_info['progress_remark'])

# ३. लॉगिन लॉजिक
def main():
    # येथे तुमचा Google Sheet चा डेटा लोड करण्याचे लॉजिक येईल
    # सध्या आपण सॅम्पल डेटा घेऊया
    data = {
        "VC101": {"password": "123", "name": "Arjun", "level": "Level 2", "fees": "Paid", "attendance": 92, "progress_remark": "गणिताचा वेग वाढला आहे, सराव चालू ठेवा!"},
        "VC102": {"password": "456", "name": "Sia", "level": "Vedic Math 1", "fees": "Pending", "attendance": 85, "progress_remark": "पाढे पाठ करणे आवश्यक आहे."}
    }

    st.sidebar.title("🔐 लॉगिन करा")
    sid = st.sidebar.text_input("विद्यार्थी ID (Student ID)")
    pwd = st.sidebar.text_input("पासवर्ड", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if sid in data and data[sid]["password"] == pwd:
            st.session_state["logged_in"] = True
            st.session_state["student_info"] = data[sid]
        else:
            st.sidebar.error("चुकीचा ID किंवा पासवर्ड!")

    # स्क्रीनवर काय दाखवायचे ते ठरवणे
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        student_dashboard(st.session_state["student_info"])
    else:
        public_home()

if __name__ == "__main__":
    main()