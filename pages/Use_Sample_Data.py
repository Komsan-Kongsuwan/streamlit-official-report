import os

# ✅ Button for using sample data
if st.button("Use Sample Data"):
    sample_file = os.path.join(os.getcwd(), "official_raw_data.xlsx")
    if os.path.exists(sample_file):
        df_sample = pd.read_excel(sample_file)
        st.session_state["official_data"] = df_sample
        st.success("✅ Sample data loaded successfully. Go to Chart page to view it!")
    else:
        st.error("❌ Sample file 'official_raw_data.xlsx' not found in working folder.")
