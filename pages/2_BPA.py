import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown(
    """
    <h1 style='margin-bottom: 0.5rem;'>📈 Chart Visualization Revenue</h1>
    """,
    unsafe_allow_html=True
)

if "official_data" not in st.session_state:
    st.warning("⚠️ Official data not found. Generate the official report first.")
    st.stop()

df_raw = st.session_state["official_data"].copy()
df_raw = df_raw[df_raw['Site'] == "BPA"]
df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
df_raw['Period'] = df_raw['Year'] + "-" + df_raw['Month']
df_raw['Period'] = pd.to_datetime(df_raw['Period'], format="%Y-%m")

st.markdown("## Trend Comparison by Item Detail")

# เปลี่ยนเป็นกรองตาม Item Detail
items = sorted(df_raw['Item Detail'].dropna().unique())
selected_items = st.multiselect("Select Item(s) to compare", items, default=["Revenue"])

if not selected_items:
    st.info("Select at least one item.")
    st.stop()

# กรองจาก Item Detail
plot_df = (
    df_raw[df_raw['Item Detail'].isin(selected_items)]
    .groupby(['Item Detail', 'Period'], as_index=False)['Amount']
    .sum()
)

# วาดกราฟ
fig = px.line(
    plot_df,
    x='Period',
    y='Amount',
    color='Item Detail',
    title="Revenue Trend by Item Detail",
    markers=True
)
fig.update_layout(xaxis_title="Period", yaxis_title="Amount")
st.plotly_chart(fig, use_container_width=True)
