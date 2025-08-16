import streamlit as st
import pandas as pd
import time

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
