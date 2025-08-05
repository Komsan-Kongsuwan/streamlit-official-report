import streamlit as st

# --- Auth ---
USERNAME = "admin"
PASSWORD = "report123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")
    if login:
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect credentials")
    st.stop()

# --- Upload Page ---
st.title("📁 Upload Excel Files")
st.markdown("Please upload your monthly Excel reports (multiple files allowed).")

#uploaded = st.file_uploader("Upload .xlsx files", type="xlsx", accept_multiple_files=True)

#if uploaded:
#    st.session_state.uploaded_files = uploaded
#    st.success("✅ Files uploaded successfully! Now go to a report page (left menu).")

if st.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()
