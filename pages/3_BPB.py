# 🔧 กำหนดรายการ Item Detail ที่ต้องการแสดง
item_order = [
    "[1045]-Revenue Total",
    "[1046]-Cost Total",
    "[1047]-Variable Cost",
    "[1048]-Marginal Profit",
    "[1049]-Fix Cost",
    "[1050]-Gross Profit",
    "[1051]-Expense Total",
    "[1052]-Operating Profit"
]

# ✅ กรองข้อมูลเฉพาะที่อยู่ในรายการ
df_selected = df_raw[df_raw['Item Detail'].isin(item_order)].copy()

# 🔁 หาชื่อเดือนล่าสุดและก่อนหน้า
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
    this_month_val = df_selected[(df_selected['Period'] == latest_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
    last_month_val = df_selected[(df_selected['Period'] == prior_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
    diff = this_month_val - last_month_val
    pct = (diff / last_month_val * 100) if last_month_val != 0 else 0

    rating = get_star_rating(pct)
    comparison_data.append({
        "Item": item.split("]-")[-1],  # 🔍 ตัด prefix [xxxx]-
        "Current": f"{this_month_val:,.0f} THB",
        "Previous": f"{last_month_val:,.0f} THB",
        "Diff": f"{diff:+,.0f} THB",
        "Pct": f"{pct:+.2f} %",
        "Month1": latest_month.strftime("%b-%Y"),
        "Month2": prior_month.strftime("%b-%Y"),
        "Color": "green" if diff >= 0 else "red",
        "Rating": rating
    })

# 🎨 แสดงผลด้วย CSS และแบ่งเป็น 2 แถว (4 คอลัมน์)
st.markdown("### 📊 Monthly Comparison Summary")

row_chunks = [comparison_data[i:i+4] for i in range(0, len(comparison_data), 4)]

for row in row_chunks:
    cols = st.columns(4)
    for col, data in zip(cols, row):
        col.markdown(f"""
        <div style="border:2px solid #ccc; border-radius:12px; padding:15px; background-color:#f9f9f9; box-shadow: 2px 2px 6px rgba(0,0,0,0.1);">
            <h5 style="margin-bottom:8px; color:#333;">
                <b>{data['Item']} {data['Rating']}</b>
            </h5>
            <p style="margin:2px 0;"><b>{data['Month2']}:</b> <span style="color:green;">{data['Previous']}</span></p>
            <p style="margin:2px 0;"><b>{data['Month1']}:</b> <span style="color:blue;">{data['Current']}</span></p>
            <p style="margin-top:8px; color:{data['Color']}; font-weight:bold;">
                {data['Pct']} = {data['Diff']}
            </p>
        </div>
        """, unsafe_allow_html=True)
