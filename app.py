import streamlit as st
import pandas as pd
import numpy as np
import calendar
import io
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

# --- App config ---
st.set_page_config(page_title="Monthly Report Processor", layout="wide")

# --- Credentials ---
USERNAME = "admin"
PASSWORD = "report123"

# --- Login Function ---
def check_login():
    st.title("🔐 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect username or password")

# --- Auth State ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    check_login()
    st.stop()

# --- Main App ---
st.title("📊 Monthly Report Generator")

uploaded_files = st.file_uploader(
    "Upload multiple Excel files", type="xlsx", accept_multiple_files=True
)

progress_bar = st.progress(0)
status_text = st.empty()
output = st.empty()

def process_files(files):
    df_list = []
    for i, file in enumerate(files):
        filename = file.name
        status_text.text(f"Processing {filename} ({i+1}/{len(files)})")

        month = filename[4:6]
        year = filename[0:4]

        header = pd.read_excel(file, nrows=3, header=None)
        last_col_index = header.iloc[2].tolist().index("Total") if "Total" in header.iloc[2].tolist() else None
        usecols = list(range(last_col_index)) if last_col_index is not None else None

        df = pd.read_excel(file, skiprows=2, nrows=49, usecols=usecols)
        df.columns.values[0:3] = ['Type', 'Item', 'Item Detail']
        df_long = df.melt(id_vars=['Type', 'Item', 'Item Detail'], var_name='Site', value_name='Amount')
        df_long['Month'] = month
        df_long['Year'] = year
        df_list.append(df_long)
        progress_bar.progress(int((i + 1) / len(files) * 100))

    df_final = pd.concat(df_list, ignore_index=True)
    df_final['Amount'] = pd.to_numeric(df_final['Amount'], errors='coerce').fillna(0)
    df_final['Month'] = df_final['Month'].astype(str).str.zfill(2)
    month_map = {f"{i:02d}": calendar.month_abbr[i] for i in range(1, 13)}

    pivot_df = pd.pivot_table(
        df_final,
        index=['Site', 'Item Detail', 'Year'],
        columns='Month',
        values='Amount',
        aggfunc='sum',
        fill_value=0,
        observed=False
    )
    pivot_df['Grand Total'] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.reset_index()
    pivot_df = pivot_df.rename(columns=month_map)

    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    final_columns = ['Site', 'Item Detail', 'Year'] + month_names + ['Grand Total']
    pivot_df = pivot_df.reindex(columns=final_columns)

    return pivot_df

if uploaded_files:
    df_result = process_files(uploaded_files)
    st.success("✅ Processing Complete!")
    st.dataframe(df_result.head())

    # Step 1: Save to temp file
    buffer = io.BytesIO()
    temp_file_name = "temp_report.xlsx"

    with pd.ExcelWriter(temp_file_name, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Report")

    # Step 2: Reopen and format with openpyxl
    wb = load_workbook(temp_file_name)
    ws = wb["Report"]

    col_index_map = {col: idx + 1 for idx, col in enumerate(df_result.columns)}
    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    number_cols = month_names + ['Grand Total']

    for col in number_cols:
        col_idx = col_index_map.get(col)
        if col_idx:
            col_letter = get_column_letter(col_idx)
            for cell in ws[col_letter][1:]:  # skip header
                cell.number_format = '#,##0_);[Red](#,##0)'

    item_col_letter = get_column_letter(col_index_map['Item Detail'])
    ws.column_dimensions[item_col_letter].width = 35

    year_col_letter = get_column_letter(col_index_map['Year'])
    for cell in ws[year_col_letter][1:]:
        cell.alignment = Alignment(horizontal='center')

    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions

    # Step 3: Save final file to buffer
    final_buffer = io.BytesIO()
    wb.save(final_buffer)
    final_buffer.seek(0)

    # Step 4: Download
    st.download_button(
        label="📥 Download Excel Report (Formatted)",
        data=final_buffer,
        file_name="official_monthly_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- Logout ---
st.markdown("---")
if st.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()

