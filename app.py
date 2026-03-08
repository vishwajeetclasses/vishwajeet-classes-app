import streamlit as st
import pandas as pd

# १. पेज कॉन्फिगरेशन
st.set_page_config(page_title="Vishwajeet Classes", layout="centered")

# २. गुगल शीट कनेक्शन फंक्शन
def load_data():
    # तुमची शीटची लिंक येथे पेस्ट करा
    sheet_url = "तुमची_पूर्ण_शीट_लिंक_येथे_टाका"
    
    # लिंकला CSV फॉरमॅटमध्ये रूपांतरित करणे
    if "edit" in sheet_url:
        csv_url = sheet_url.split('/edit')[0] + '/export?format=csv'
    else:
        csv_url = sheet_url
        
    try:
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"शीट लोड करताना एरर आला: {e}")
        return None

def main():
    df = load_data()
    
    if df is not None:
        # लॉगिनसाठी डेटा तयार करणे
        # तुमच्या शीटमध्ये student_id, password, name हे कॉलम असावेत
        data_dict = df.set_index('student_id').to_dict('index')

        st.sidebar.title("🔐 विद्यार्थी लॉगिन")
        sid = st.sidebar.text_input("विद्यार्थी ID (उदा. VC101)")
        pwd = st.sidebar.text_input("पासवर्ड", type="password")
        
        if st.sidebar.button("Login"):
            if sid in data_dict and str(data_dict[sid]["password"]) == str(pwd):
                st.session_state["logged_in"] = True
                st.session_state["info"] = data_dict[sid]
            else:
                st.sidebar.error("ID किंवा पासवर्ड चुकीचा आहे!")

        # लॉगिन नंतरचे डॅशबोर्ड
        if st.session_state.get("logged_in"):
            info = st.session_state["info"]
            st.title(f"🚩 स्वागत आहे, {info['name']}!")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("चालू लेव्हल", info['level'])
                st.metric("हजेरी", f"{info['attendance']}%")
            with col2:
                st.subheader("फी स्टेटस")
                if info['fees'].lower() == "paid":
                    st.success("Paid")
                else:
                    st.error("Pending")
            
            st.divider()
            st.info(f"📝 **शिक्षकांचा अभिप्राय:** {info['progress_remark']}")
            
            if st.sidebar.button("Logout"):
                st.session_state["logged_in"] = False
                st.rerun()
        else:
            # पब्लिक होम पेज
            st.title("विश्वजीत क्लासेस (Vishwajeet Classes)")
            st.write("अ‍ॅबॅकस आणि वैदिक गणित केंद्र")
            st.image("https://via.placeholder.com/700x300?text=Vishwajeet+Classes+Welcome", use_column_width=True)
            st.write("तुमच्या मुलाची प्रगती पाहण्यासाठी डावीकडील मेन्यू मधून लॉगिन करा.")

if __name__ == "__main__":
    main()
