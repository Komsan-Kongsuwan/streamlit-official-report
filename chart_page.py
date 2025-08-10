# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page(site_code):
    st.title(f"📈 Chart Visualization - {site_code}")
