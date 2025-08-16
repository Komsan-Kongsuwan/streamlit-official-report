
"""
import os
import streamlit as st
import pandas as pd

sample_file = os.path.join(os.getcwd(), "official_raw_data.xlsx")
if os.path.exists(sample_file):
    df_sample = pd.read_excel(sample_file)
    st.session_state["official_data"] = df_sample
    st.session_state.pop("selected_site", None)  # force re-initialize on next chart render
    st.success("✅ Sample data loaded successfully. Go to Chart page to view it!")
else:
    st.error("❌ Sample file 'official_raw_data.xlsx' not found in working folder.")
"""


import streamlit as st
import pandas as pd
import time

if st.button("📂 Load Sample Data"):
    progress = st.progress(0, text="Loading sample data...")

    # Step 1: Read file
    progress.progress(20, text="Reading Excel file...")
    df = pd.read_excel("official_raw_data.xlsx")
    time.sleep(0.5)

    # Step 2: Normalize Year/Month
    progress.progress(50, text="Processing Year/Month...")
    df['Year'] = df['Year'].astype(int).astype(str)
    df['Month'] = df['Month'].astype(int).astype(str).str.zfill(2)
    time.sleep(0.5)

    # Step 3: Create Period
    progress.progress(80, text="Creating Period column...")
    df['Period'] = pd.to_datetime(df['Year'] + "-" + df['Month'], format="%Y-%m")
    time.sleep(0.5)

    # Step 4: Save to session state
    st.session_state["official_data"] = df
    progress.progress(100, text="✅ Done!")

    st.success("Sample data loaded successfully.")
