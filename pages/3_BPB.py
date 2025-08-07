import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Chart Visualization By Item Detail")

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
items = sorted(df_raw['Item Detail'].dropna().unique())
selected_items = st.multiselect("Select Item Detail", items, default=["[1002]-Revenue"])

if not selected_items:
    st.info("Select at least one item.")
    st.stop()

line_df = (
    df_raw[df_raw['Item Detail'].isin(selected_items)]
    .groupby(['Item Detail', 'Period'], as_index=False)['Amount']
    .sum()
)

fig_line = px.line(
    line_df,
    x='Period',
    y='Amount',
    color='Item Detail',
    title="Monthly",
    markers=True
)

fig_line.update_layout(xaxis_title = "", yaxis_title="Amount (THB)")
st.plotly_chart(fig_line, use_container_width=True)

# --- Bar Chart: Total Revenue by Item Detail ---
bar_df = (
    df_raw[df_raw['Item Detail'].isin(selected_items)]
    .groupby(['Year'], as_index=False)['Amount']
    .sum()
    .sort_values(by='Amount', ascending=False)
)

fig_bar = px.bar(
    bar_df,
    x='Year',
    y='Amount',
    title="Yearly",
    text_auto='.2s'
)
fig_bar.update_layout(xaxis_title = "", yaxis_title="Total Amount (THB)")
st.plotly_chart(fig_bar, use_container_width=True)






import datetime

# Step 1: Filter only selected items
latest_df = df_raw[df_raw['Item Detail'].isin(selected_items)]

# Step 2: Get the latest 2 months from data
latest_month = latest_df['Period'].max()
prior_month = latest_month - pd.DateOffset(months=1)

# Step 3: Prepare summary
comparison_data = []

for item in selected_items:
    this_month_val = latest_df[(latest_df['Period'] == latest_month) & (latest_df['Item Detail'] == item)]['Amount'].sum()
    last_month_val = latest_df[(latest_df['Period'] == prior_month) & (latest_df['Item Detail'] == item)]['Amount'].sum()
    diff = this_month_val - last_month_val
    pct = (diff / last_month_val * 100) if last_month_val != 0 else 0

    comparison_data.append({
        "Item": item.replace('[1002]-', '').strip(),  # Clean prefix if needed
        "Current": f"{this_month_val:,.0f} THB",
        "Previous": f"{last_month_val:,.0f} THB",
        "Diff": f"{diff:+,.0f} THB",
        "Pct": f"{pct:+.2f} %",
        "Month1": latest_month.strftime("%b-%Y"),
        "Month2": prior_month.strftime("%b-%Y"),
    })

# Step 4: Display using st.columns()
st.markdown("### 🔍 Monthly Comparison")

cols = st.columns(len(comparison_data))
for col, data in zip(cols, comparison_data):
    color = "green" if "-" not in data["Diff"] else "red"
    col.markdown(f"""
    <div style="border:1px solid #ccc; padding:10px; border-radius:10px; background-color:#f5f9f9;">
        <h4 style="margin-bottom:5px;">{data['Item']}</h4>
        <p style="margin:0;"><b>{data['Month2']}</b>: <span style='color:green;'>{data['Previous']}</span></p>
        <p style="margin:0;"><b>{data['Month1']}</b>: <span style='color:blue;'>{data['Current']}</span></p>
        <p style="margin-top:5px; color:{color}; font-weight:bold;">
            {data['Pct']} = {data['Diff']}
        </p>
    </div>
    """, unsafe_allow_html=True)
