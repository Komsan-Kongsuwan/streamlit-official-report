# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page(site_code):
    st.title(f"📈 Chart Visualization - {site_code}")

    if "official_data" not in st.session_state:
        st.warning("⚠️ Official data not found. Generate the official report first.")
        st.stop()

    df_raw = st.session_state["official_data"].copy()
    df_raw = df_raw[df_raw['Site'] == site_code]
    df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
    df_raw['Period'] = pd.to_datetime(df_raw['Year'] + "-" + df_raw['Month'], format="%Y-%m")

    # --- Line Chart ---
    items = sorted(df_raw['Item Detail'].dropna().unique())
    selected_items = st.multiselect("Select Item Detail", items, default=["[1002]-Revenue"])
    if not selected_items:
        st.info("Select at least one item.")
        st.stop()

    line_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
        .groupby(['Item Detail', 'Period'], as_index=False)['Amount'].sum()

    fig_line = px.line(
        line_df,
        x='Period',
        y='Amount',
        color='Item Detail',
        title="Monthly",
        markers=True
    )
    fig_line.update_layout(
        hovermode="x",
        hoverdistance=100,
        spikedistance=-1,
        xaxis=dict(
            showspikes=True,
            spikecolor="red",
            spikethickness=2,
            spikemode="across"
        ),
        hoverlabel=dict(
            bgcolor="black",
            font_size=14,
            font_color="white"
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Bar Chart ---
    bar_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
        .groupby(['Year'], as_index=False)['Amount'].sum() \
        .sort_values(by='Amount', ascending=False)

    fig_bar = px.bar(
        bar_df,
        x='Year',
        y='Amount',
        title="Yearly",
        text_auto='.2s'
    )
    fig_bar.update_layout(xaxis_title="", yaxis_title="Total Amount (THB)")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Monthly Comparison Summary ---
    item_order = [
        "[1045]-Revenue Total", "[1046]-Cost Total",
        "[1047]-Variable Cost", "[1048]-Marginal Profit",
        "[1049]-Fix Cost", "[1050]-Gross Profit",
        "[1051]-Expense Total", "[1052]-Operate Profit"
    ]
    df_selected = df_raw[df_raw['Item Detail'].isin(item_order)].copy()
    latest_month = df_selected['Period'].max()
    prior_month = latest_month - pd.DateOffset(months=1)

    cost_items = {"[1046]-Cost Total", "[1047]-Variable Cost", "[1049]-Fix Cost", "[1051]-Expense Total"}

    def get_star_rating(pct, is_cost=False, this_month_val=0, last_month_val=0):
        diff = this_month_val - last_month_val
        pct = (diff / last_month_val * 100) if last_month_val != 0 else 0
        if is_cost:
            if pct < -100: return "⭐⭐⭐⭐"
            elif pct <= -50: return "⭐⭐⭐"
            elif pct <= -25: return "⭐⭐"
            elif pct <= 0: return "⭐"
            elif pct <= 25: return "🚨"
            elif pct <= 50: return "🚨🚨"
            elif pct <= 75: return "🚨🚨🚨"
            else: return "🚨🚨🚨🚨" 
            
    comparison_data = []
    for item in item_order:
        this_month_val = df_selected[(df_selected['Period'] == latest_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
        last_month_val = df_selected[(df_selected['Period'] == prior_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
        diff = this_month_val - last_month_val
        pct = (diff / last_month_val * 100) if last_month_val != 0 else 0

        is_cost = item in cost_items
        rating = get_star_rating(pct, is_cost=is_cost, this_month_val=this_month_val, last_month_val=last_month_val)
        
        # ปรับ Arrow และสีให้รองรับค่าติดลบ
        if is_cost:
            if this_month_val > last_month_val:
                arrow = "▲"
                color = "red"
            elif this_month_val < last_month_val:
                arrow = "▼"
                color = "green"
            else:
                arrow = ""
                color = "black"
        else:  # profit items
            if this_month_val > last_month_val:
                arrow = "▲"
                color = "green"
            elif this_month_val < last_month_val:
                arrow = "▼"
                color = "red"
            else:
                arrow = ""
                color = "black"

        
        comparison_data.append({
            "Item": item.split("]-")[-1],
            "Current": f"{this_month_val:,.0f} THB",
            "Previous": f"{last_month_val:,.0f} THB",
            "Diff": f"{abs(diff):,.0f} THB",  # ตัดเครื่องหมายออก
            "Pct": f"{abs(pct):.2f} %",
            "Arrow": arrow,
            "Month1": latest_month.strftime("%b-%Y"),
            "Month2": prior_month.strftime("%b-%Y"),
            "Color": color,
            "Rating": rating
        })

    st.markdown("### 📊 Monthly Comparison Summary")
    row_chunks = [comparison_data[i:i+4] for i in range(0, len(comparison_data), 4)]
    for row in row_chunks:
        cols = st.columns(4)
        for col, data in zip(cols, row):
            col.markdown(f"""
            <div style="border:2px solid #ccc; border-radius:12px; padding:15px; background-color:#f9f9f9; box-shadow: 2px 2px 6px rgba(0,0,0,0.1);">
                <h5 style="margin-bottom:8px; color:#333;">
                    {data['Item']} {data['Rating']}
                </h5>
                <p style="margin:2px 0;"><b>{data['Month2']}:</b> <span style="color:green;">{data['Previous']}</span></p>
                <p style="margin:2px 0;"><b>{data['Month1']}:</b> <span style="color:blue;">{data['Current']}</span></p>
                <p style="margin-top:8px; color:{data['Color']}; font-weight:bold;">
                    {data['Arrow']} {data['Pct']} = {data['Diff']}
                </p>
            </div>
            <br>
            """, unsafe_allow_html=True)
