import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Chart Visualization Revenue")

# --- Load session data ---
if "official_data" not in st.session_state:
    st.warning("⚠️ Official data not found. Generate the official report first.")
    st.stop()

df_raw = st.session_state["official_data"].copy()
df_raw = df_raw[df_raw['Site'] == "BPB"]
df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
df_raw['Period'] = df_raw['Year'] + "-" + df_raw['Month']
df_raw['Period'] = pd.to_datetime(df_raw['Period'], format="%Y-%m")

# --- Line Chart: Trend Comparison ---
st.markdown("## 📉 Trend Comparison (Line Chart)")
items = sorted(df_raw['Item Detail'].dropna().unique())
selected_items = st.multiselect("Select items to compare", items, default=["Revenue"])

if not selected_items:
    st.info("Select at least one item.")
    st.stop()

line_df = (
    df_raw[df_raw['Item Detail'].isin(selected_items)]
    .groupby(['Item Detail', 'Period'], as_index=False)['Amount']
    .sum()
)

fig_line = px.bar(
    line_df,
    x='Period',
    y='Amount',
    color='Item Detail',
    title="Monthly Trend",
    markers=True
)
fig_line.update_layout(xaxis_title="Period", yaxis_title="Amount")
st.plotly_chart(fig_line, use_container_width=True)

# --- Bar Chart: Total Revenue by Item Detail ---
st.markdown("## 📊 Total Revenue by Item Detail (Bar Chart)")
bar_df = (
    df_raw[df_raw['Item Detail'].isin(selected_items)]
    .groupby(['Item Detail'], as_index=False)['Amount']
    .sum()
    .sort_values(by='Amount', ascending=False)
)

fig_bar = px.bar(
    bar_df,
    x='Period',
    y='Amount',
    title="Total Revenue by Item Detail",
    text_auto='.2s'
)
fig_bar.update_layout(xaxis_title="Item Detail", yaxis_title="Total Amount")
st.plotly_chart(fig_bar, use_container_width=True)
