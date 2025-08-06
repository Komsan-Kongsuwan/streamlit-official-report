import streamlit as st

st.set_page_config(page_title="Monthly Report Hub", layout="wide")
st.title("📁 Monthly Report Dashboard")

st.markdown("Welcome! Please upload your Excel files, then go to 'Official Monthly Report' to generate and visualize.")
uploaded = st.file_uploader("📤 Upload .xlsx files", type="xlsx", accept_multiple_files=True)

if uploaded:
    st.session_state.uploaded_files = uploaded
    st.success("✅ Files uploaded successfully! Now go to the 'Official Monthly Report' page in sidebar.")
