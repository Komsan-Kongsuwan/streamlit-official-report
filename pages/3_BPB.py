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






# 🔧 กำหนดรายการ Item Detail ที่ต้องการแสดง
item_order = [
    "[1045]-Revenue Total",
@@ -83,6 +17,19 @@
latest_month = df_selected['Period'].max()
prior_month = latest_month - pd.DateOffset(months=1)

# ⭐ ฟังก์ชันให้ rating เป็นดาว
def get_star_rating(pct):
    if pct < 0:
        return "⭐"
    elif pct <= 25:
        return "⭐⭐"
    elif pct <= 50:
        return "⭐⭐⭐"
    elif pct <= 100:
        return "⭐⭐⭐⭐"
    else:
        return "⭐⭐⭐⭐⭐"

# 🧮 เตรียมข้อมูลเปรียบเทียบ
comparison_data = []
for item in item_order:
@@ -91,6 +38,7 @@
    diff = this_month_val - last_month_val
    pct = (diff / last_month_val * 100) if last_month_val != 0 else 0

    rating = get_star_rating(pct)
    comparison_data.append({
        "Item": item.split("]-")[-1],  # 🔍 ตัด prefix [xxxx]-
        "Current": f"{this_month_val:,.0f} THB",
@@ -99,7 +47,8 @@
        "Pct": f"{pct:+.2f} %",
        "Month1": latest_month.strftime("%b-%Y"),
        "Month2": prior_month.strftime("%b-%Y"),
        "Color": "green" if diff >= 0 else "red"
        "Color": "green" if diff >= 0 else "red",
        "Rating": rating
    })

# 🎨 แสดงผลด้วย CSS และแบ่งเป็น 2 แถว (4 คอลัมน์)
@@ -112,13 +61,13 @@
    for col, data in zip(cols, row):
        col.markdown(f"""
        <div style="border:2px solid #ccc; border-radius:12px; padding:15px; background-color:#f9f9f9; box-shadow: 2px 2px 6px rgba(0,0,0,0.1);">
            <h5 style="margin-bottom:8px; color:#333;">📌 <b>{data['Item']}</b></h5>
            <h5 style="margin-bottom:8px; color:#333;">
                <b>{data['Item']} {data['Rating']}</b>
            </h5>
            <p style="margin:2px 0;"><b>{data['Month2']}:</b> <span style="color:green;">{data['Previous']}</span></p>
            <p style="margin:2px 0;"><b>{data['Month1']}:</b> <span style="color:blue;">{data['Current']}</span></p>
            <p style="margin-top:8px; color:{data['Color']}; font-weight:bold;">
                {data['Pct']} = {data['Diff']}
            </p>
        </div>
        <br>
        """, unsafe_allow_html=True
