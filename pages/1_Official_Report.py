import streamlit as st
import pandas as pd
import calendar
import io
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

st.title("📊 Official Monthly Report")

if "uploaded_files" not in st.session_state:
    st.warning("⚠️ Please upload files from the homepage first.")
    st.stop()

uploaded_files = st.session_state.uploaded_files

def generate_official_report(files):
    df_list = []
    progress_bar = st.progress(0)
    for i, file in enumerate(files):
        progress_bar.progress(int((i + 1) / len(files) * 100))
        filename = file.name
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

    final_columns = ['Site', 'Item Detail', 'Year'] + list(month_map.values()) + ['Grand Total']
    pivot_df = pivot_df.reindex(columns=final_columns)
    return pivot_df

def format_and_download(df_result):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="Report")

    wb = load_workbook(buffer)
    ws = wb["Report"]

    col_index_map = {col: idx + 1 for idx, col in enumerate(df_result.columns)}
    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    number_cols = month_names + ['Grand Total']

    for col in number_cols:
        col_idx = col_index_map.get(col)
        col_letter = get_column_letter(col_idx)
        for cell in ws[col_letter][1:]:
            cell.number_format = '#,##0_);[Red](#,##0)'

    if 'Item Detail' in col_index_map:
        ws.column_dimensions[get_column_letter(col_index_map['Item Detail'])].width = 35
    if 'Year' in col_index_map:
        for cell in ws[get_column_letter(col_index_map['Year'])][1:]:
            cell.alignment = Alignment(horizontal='center')

    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions

    final_buffer = io.BytesIO()
    wb.save(final_buffer)
    final_buffer.seek(0)

    st.download_button(
        label="📥 Download Official Monthly Report",
        data=final_buffer,
        file_name="official_monthly_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

df_result = generate_official_report(uploaded_files)
st.success("✅ Official Report Ready")
st.dataframe(df_result.head())
format_and_download(df_result)
