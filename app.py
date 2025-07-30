import streamlit as st
import pandas as pd
import numpy as np
import calendar
import io

st.set_page_config(page_title="Monthly Report Processor", layout="wide")
st.title("📊 Official Monthly Report Generator")

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

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Report")

    st.download_button(
        label="📥 Download Excel Report",
        data=buffer.getvalue(),
        file_name="official_monthly_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )