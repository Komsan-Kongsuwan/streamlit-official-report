import streamlit as st

st.set_page_config(page_title="Monthly Report Hub", layout="wide")
st.title("📁 Monthly Report Generator")

uploaded = st.file_uploader("📤 Upload .xlsx files", type="xlsx", accept_multiple_files=True)

if uploaded:
    st.session_state.uploaded_files = uploaded
    st.success("✅ Files uploaded successfully! Now choose a report page from the sidebar.")

if "uploaded_files" not in st.session_state:
    st.warning("⚠️ Please upload Excel files before proceeding to the report pages.")
