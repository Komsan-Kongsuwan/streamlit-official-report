# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    # Reduce top margin/padding of the page
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <h6 style='margin-top:0; margin-bottom:0.5rem; color:#333;'>
            🕵️‍♂️ Official Report Analysis
        </h6>
    """, unsafe_allow_html=True)


    if "official_data" not in st.session_state:
        st.warning("⚠️ Official data not found. Generate the official report first.")
        st.stop()

    df_raw = st.session_state["official_data"].copy()
    df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
    df_raw['Period'] = pd.to_datetime(df_raw['Year'] + "-" + df_raw['Month'], format="%Y-%m")

    # --- Sidebar: Site selection ---
    sites = sorted(df_raw['Site'].dropna().unique())
    if "selected_site" not in st.session_state:
        st.session_state.selected_site = sites[0]
    for site in sites:
        if st.sidebar.button(site, use_container_width=True):
            st.session_state.selected_site = site

    site_code = st.session_state.selected_site
    st.subheader(f"📊 Analysis for site: **{site_code}**")

    # --- Filter data ---
    df_raw = df_raw[df_raw['Site'] == site_code]

    # --- Monthly Comparison Summary ---
    item_order = [
        "[1045]-Revenue Total", "[1046]-Variable Cost",
        "[1047]-Marginal Profit", "[1048]-Fix Cost",
        "[1049]-Cost Total", "[1050]-Gross Profit",
        "[1051]-Expense Total", "[1052]-Operate Profit"
    ]
    df_selected = df_raw[df_raw['Item Detail'].isin(item_order)].copy()
    latest_month = df_selected['Period'].max()
    prior_month = latest_month - pd.DateOffset(months=1)
    cost_items = {"[1049]-Cost Total", "[1046]-Variable Cost", "[1048]-Fix Cost", "[1051]-Expense Total"}

    def get_star_rating(is_cost=False, this_month_val=0, last_month_val=0):
        diff = this_month_val - last_month_val
        pct = (diff / last_month_val * 100) if last_month_val != 0 else 0
        if is_cost:
            if pct < -30: return "⭐⭐⭐⭐"
            elif pct <= -20: return "⭐⭐⭐"
            elif pct <= -10: return "⭐⭐"
            elif pct <= 0: return "⭐"
            elif pct <= 10: return "🚨"
            elif pct <= 20: return "🚨🚨"
            elif pct <= 30: return "🚨🚨🚨"
            else: return "🚨🚨🚨🚨"
        else:
            if this_month_val > 0:
                if pct > 50: return "⭐⭐⭐⭐"
                elif pct >= 25: return "⭐⭐⭐"
                elif pct >= 5: return "⭐⭐"
                elif pct >= 0: return "⭐"
                elif pct >= -5: return "🚨"
                elif pct >= -25: return "🚨🚨"
                elif pct >= -50: return "🚨🚨🚨"
                else: return "🚨🚨🚨🚨"
            else:
                if this_month_val > -5000: return "🚨"
                elif this_month_val >= -50000: return "🚨🚨"
                elif this_month_val >= -100000: return "🚨🚨🚨"
                elif this_month_val >= -500000: return "🚨🚨🚨🚨"
                else: return "🚨🚨🚨🚨"

    comparison_data = []
    for item in item_order:
        this_month_val = df_selected[(df_selected['Period'] == latest_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
        last_month_val = df_selected[(df_selected['Period'] == prior_month) & (df_selected['Item Detail'] == item)]['Amount'].sum()
        diff = this_month_val - last_month_val
        pct = (diff / last_month_val * 100) if last_month_val != 0 else 0
        is_cost = item in cost_items
        rating = get_star_rating(is_cost=is_cost, this_month_val=this_month_val, last_month_val=last_month_val)
        arrow, color = ("▲", "red") if (is_cost and this_month_val > last_month_val) else \
                       ("▼", "green") if is_cost else \
                       ("▲", "green") if this_month_val > last_month_val else ("▼", "red")

        comparison_data.append({
            "Item": item.split("]-")[-1],
            "Current": f"{this_month_val:,.0f} THB",
            "Previous": f"{last_month_val:,.0f} THB",
            "Diff": f"{abs(diff):,.0f} THB",
            "Pct": f"{abs(pct):.2f} %",
            "Arrow": arrow,
            "Month1": latest_month.strftime("%b-%Y"),
            "Month2": prior_month.strftime("%b-%Y"),
            "Color": color,
            "Rating": rating
        })

    st.markdown(f"### 🆗🆖 Comparison {prior_month.strftime('%b %Y')} vs {latest_month.strftime('%b %Y')}")

    row_chunks = [comparison_data[i:i+4] for i in range(0, len(comparison_data), 4)]
    for row in row_chunks:
        cols = st.columns(4)
        for col, data in zip(cols, row):
            col.markdown(f"""
            <div style="border:1px solid #aaa; border-radius:8px; padding:8px; 
                        background-color:#fdfdfd; font-size:12px; line-height:1.2;">
                <b style="color:#333;">{data['Item']} {data['Rating']}</b><br>
                <span style="color:green;">{data['Month2']}:</span> {data['Previous']}<br>
                <span style="color:blue;">{data['Month1']}:</span> {data['Current']}<br>
                <span style="color:{data['Color']}; font-weight:bold;">
                    {data['Arrow']} {data['Pct']} = {data['Diff']}
                </span>
            </div>
            """, unsafe_allow_html=True)

    # --- Line & Bar Chart Side by Side (70:30 layout) ---
    items = sorted(df_raw['Item Detail'].dropna().unique())
    selected_items = st.multiselect("Select Item Detail Chart", items, default=["[1045]-Revenue Total"])
    if not selected_items:
        st.info("Select at least one item.")
        st.stop()
    selected_items_display = [item.split(']-', 1)[-1] for item in selected_items]

    col1, col2 = st.columns([6, 4])  # 70% line chart, 30% bar chart

    with col1:
        st.markdown(f"### 📈 {', '.join(selected_items_display)} - Line Chart")
        line_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
            .groupby(['Item Detail', 'Period'], as_index=False)['Amount'].sum()
        fig_line = px.line(line_df, x='Period', y='Amount', color='Item Detail', markers=True)
        fig_line.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=40, b=20),
            showlegend=False  # 🔹 remove legend
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        st.markdown(f"### 📊 {', '.join(selected_items_display)} - Bar Chart")
        bar_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
            .groupby(['Item Detail', 'Year'], as_index=False)['Amount'].sum()
        fig_bar = px.bar(bar_df, x='Year', y='Amount', color='Item Detail', text_auto='.2s')
        fig_bar.update_layout(height=320, margin=dict(l=10, r=10, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)
