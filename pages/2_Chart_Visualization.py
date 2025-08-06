import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Chart Visualization Revenue")

if "official_data" not in st.session_state:
    st.warning("⚠️ Official data not found. Generate the official report first.")
    st.stop()

df_raw = st.session_state["official_data"].copy()
df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
df_raw['Period'] = df_raw['Year'] + "-" + df_raw['Month']
df_raw['Period'] = pd.to_datetime(df_raw['Period'], format="%Y-%m")

st.markdown("## Trend Comparison")
sites = sorted(df_raw['Site'].dropna().unique())
selected_sites = st.multiselect("Select sites to compare", sites, default=["BPA"])

if not selected_sites:
    st.info("Select at least one site.")
    st.stop()

plot_df = (
    df_raw[df_raw['Site'].isin(selected_sites)]
    .groupby(['Site', 'Period'], as_index=False)['Amount']
    .sum()
)

fig = px.line(
    plot_df,
    x='Period',
    y='Amount',
    color='Site',
    title="Revenue Trend Comparison",
    markers=True
)
fig.update_layout(xaxis_title="Period", yaxis_title="Amount")
st.plotly_chart(fig, use_container_width=True)
