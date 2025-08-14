# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("🕵️‍♂️ Official Report Analysis")

    if "official_data" not in st.session_state:
        st.warning("⚠️ Official data not found. Generate the official report first.")
        st.stop()

    df_raw = st.session_state["official_data"].copy()
    df_raw['Amount'] = pd.to_numeric(df_raw['Amount'], errors='coerce').fillna(0)
    df_raw['Period'] = pd.to_datetime(df_raw['Year'] + "-" + df_raw['Month'], format="%Y-%m")

    # --- Automated Sidebar Navigation: Dynamic site buttons ---
    st.sidebar.header("📍 Select Site")
    
    # Automatically extract unique sites from data
    available_sites = sorted(df_raw['Site'].dropna().unique())
    
    # Handle dynamic site changes (new sites added/removed)
    if "available_sites_cache" not in st.session_state:
        st.session_state.available_sites_cache = available_sites
    elif st.session_state.available_sites_cache != available_sites:
        st.session_state.available_sites_cache = available_sites
        st.info(f"🔄 Site list updated! Found {len(available_sites)} sites: {', '.join(available_sites)}")
    
    # Auto-initialize selected site
    if "selected_site" not in st.session_state or st.session_state.selected_site not in available_sites:
        st.session_state.selected_site = available_sites[0] if available_sites else None
        if available_sites:
            st.success(f"🎯 Auto-selected first available site: {st.session_state.selected_site}")
    
    if not available_sites:
        st.sidebar.warning("⚠️ No sites found in data")
        st.stop()
    
    # Display site count info
    st.sidebar.caption(f"📊 Found {len(available_sites)} sites in data")
    
    # Custom CSS for exact Streamlit page navigation styling
    st.sidebar.markdown("""
    <style>
    /* Minimize gaps between buttons */
    .stButton {
        margin: 0 !important;
        margin-bottom: 0.125rem !important;
        padding: 0 !important;
    }
    
    /* Remove default spacing from button containers */
    .stButton + .stButton {
        margin-top: 0 !important;
    }
    
    /* Style buttons to match Streamlit page navigation exactly */
    .stButton > button {
        width: 100% !important;
        padding: 0.5rem 0.75rem !important;
        margin: 0 !important;
        border: none !important;
        border-radius: 0.5rem !important;
        background-color: transparent !important;
        color: rgb(49, 51, 63) !important;
        text-align: left !important;
        font-size: 0.875rem !important;
        font-weight: 400 !important;
        line-height: 1.25rem !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        border-left: 4px solid transparent !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(151, 166, 195, 0.15) !important;
        color: rgb(49, 51, 63) !important;
        border-color: transparent !important;
    }
    
    .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }
    
    .stButton > button:active {
        background-color: rgba(151, 166, 195, 0.25) !important;
    }
    
    /* Selected state styling */
    .selected-site {
        margin: 0 !important;
        margin-bottom: 0.125rem !important;
        padding: 0 !important;
    }
    
    .selected-site button {
        background-color: rgba(255, 75, 75, 0.1) !important;
        color: rgb(255, 75, 75) !important;
        font-weight: 600 !important;
        border-left: 4px solid rgb(255, 75, 75) !important;
        margin: 0 !important;
    }
    
    .selected-site button:hover {
        background-color: rgba(255, 75, 75, 0.15) !important;
        color: rgb(255, 75, 75) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Automatically generate navigation buttons for each site
    for site_name in available_sites:
        is_selected = site_name == st.session_state.selected_site
        
        # Add selected styling wrapper
        if is_selected:
            st.sidebar.markdown('<div class="selected-site">', unsafe_allow_html=True)
        
        # Create button with unique key based on site name
        button_clicked = st.sidebar.button(
            site_name, 
            key=f"nav_btn_{site_name}",  # Dynamic key based on site name
            use_container_width=True,
            help=f"Switch to {site_name} analysis"  # Dynamic tooltip
        )
        
        # Close selected styling wrapper
        if is_selected:
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # Handle button click - automatically update selected site
        if button_clicked:
            st.session_state.selected_site = site_name
            st.sidebar.success(f"✅ Switched to: {site_name}")
            st.rerun()

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

        if is_cost:
            arrow, color = ("▲", "red") if this_month_val > last_month_val else ("▼", "green")
        else:
            arrow, color = ("▲", "green") if this_month_val > last_month_val else ("▼", "red")

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

    st.markdown(f"### 🆗🆖 Comparison {prior_month.strftime('%B %Y')} vs {latest_month.strftime('%B %Y')}")
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
            """, unsafe_allow_html=True)

    # --- Line Chart ---
    items = sorted(df_raw['Item Detail'].dropna().unique())
    selected_items = st.multiselect("Select Item Detail Chart", items, default=["[1045]-Revenue Total"])
    if not selected_items:
        st.info("Select at least one item.")
        st.stop()

    selected_items_display = [item.split(']-', 1)[-1] for item in selected_items]
    st.markdown(f"### 📈 {', '.join(selected_items_display)} - Line Chart")

    line_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
        .groupby(['Item Detail', 'Period'], as_index=False)['Amount'].sum()

    fig_line = px.line(line_df, x='Period', y='Amount', color='Item Detail', title="Monthly", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Bar Chart ---
    st.markdown(f"### 📊 {', '.join(selected_items_display)} - Bar Chart")
    bar_df = df_raw[df_raw['Item Detail'].isin(selected_items)] \
        .groupby(['Item Detail', 'Year'], as_index=False)['Amount'].sum()

    fig_bar = px.bar(bar_df, x='Year', y='Amount', color='Item Detail', title="Yearly", text_auto='.2s')
    st.plotly_chart(fig_bar, use_container_width=True)
