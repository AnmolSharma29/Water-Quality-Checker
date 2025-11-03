import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Based Water Quality Checker", page_icon="💧", layout="wide")

st.title("AI based water quality checker")
st.markdown("**Monitoring water quality trends from 2000 to 2025**")

@st.cache_data
def generate_water_quality_data():
    # Create date range from 2000 to 2025
    dates = pd.date_range(start='2000-01-01', end='2025-11-03', freq='M')
    
    # Generate realistic water quality parameters
    np.random.seed(42)
    n = len(dates)
    
    # pH (normal range: 6.5-8.5, ideal ~7.5)
    ph = 7.5 + np.random.normal(0, 0.3, n) + 0.2 * np.sin(np.arange(n) * 0.1)
    
    # TDS - Total Dissolved Solids in mg/L (acceptable: <500, ideal <300)
    tds = 250 + np.random.normal(0, 50, n) + 30 * np.sin(np.arange(n) * 0.15)
    tds = np.clip(tds, 150, 600)
    
    # Turbidity in NTU (ideal: <1, acceptable: <5)
    turbidity = 2 + np.random.normal(0, 1, n) + 1.5 * np.sin(np.arange(n) * 0.2)
    turbidity = np.clip(turbidity, 0.5, 8)
    
    # Dissolved Oxygen in mg/L (good: >6)
    do = 7 + np.random.normal(0, 0.8, n) - 0.5 * np.sin(np.arange(n) * 0.12)
    do = np.clip(do, 4, 9)
    
    # Calculate overall quality score (0-100)
    ph_score = 100 - abs(7.5 - ph) * 20
    tds_score = np.clip(100 - (tds - 200) / 5, 0, 100)
    turbidity_score = np.clip(100 - turbidity * 15, 0, 100)
    do_score = np.clip(do * 12, 0, 100)
    
    quality_score = (ph_score + tds_score + turbidity_score + do_score) / 4
    
    df = pd.DataFrame({
        'Date': dates,
        'pH': ph,
        'TDS (mg/L)': tds,
        'Turbidity (NTU)': turbidity,
        'Dissolved Oxygen (mg/L)': do,
        'Quality Score': quality_score
    })
    
    return df

# Load data
df = generate_water_quality_data()

# Sidebar for filters
st.sidebar.header("Filters")
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=2000,
    max_value=2025,
    value=(2000, 2025)
)

# Filter data based on year range
mask = (df['Date'].dt.year >= year_range[0]) & (df['Date'].dt.year <= year_range[1])
filtered_df = df[mask]

# Metrics row
st.subheader("Current Water Quality Metrics (Latest Reading)")
col1, col2, col3, col4 = st.columns(4)

latest = filtered_df.iloc[-1]

with col1:
    st.metric("pH Level", f"{latest['pH']:.2f}", 
              delta="Optimal" if 6.5 <= latest['pH'] <= 8.5 else "Outside Range")

with col2:
    st.metric("TDS", f"{latest['TDS (mg/L)']:.0f} mg/L",
              delta="Good" if latest['TDS (mg/L)'] < 300 else "Moderate")

with col3:
    st.metric("Turbidity", f"{latest['Turbidity (NTU)']:.2f} NTU",
              delta="Clear" if latest['Turbidity (NTU)'] < 5 else "Cloudy")

with col4:
    quality = latest['Quality Score']
    status = "Excellent" if quality > 80 else "Good" if quality > 60 else "Fair"
    st.metric("Quality Score", f"{quality:.0f}/100", delta=status)

# Main line chart
st.subheader("Water Quality Score Over Time")
fig = px.line(filtered_df, x='Date', y='Quality Score',
              title='Overall Water Quality Score (2000-2025)',
              labels={'Quality Score': 'Quality Score (0-100)'},
              template='plotly_white')
fig.update_traces(line_color='#1f77b4', line_width=2)
fig.add_hline(y=80, line_dash="dash", line_color="green", 
              annotation_text="Excellent Threshold")
fig.add_hline(y=60, line_dash="dash", line_color="orange", 
              annotation_text="Good Threshold")
st.plotly_chart(fig, use_container_width=True)

# Parameter selection
st.subheader("Individual Parameter Trends")
parameter = st.selectbox(
    "Select parameter to visualize:",
    ['pH', 'TDS (mg/L)', 'Turbidity (NTU)', 'Dissolved Oxygen (mg/L)']
)

fig2 = px.line(filtered_df, x='Date', y=parameter,
               title=f'{parameter} Over Time',
               template='plotly_white')
fig2.update_traces(line_color='#2ca02c', line_width=2)
st.plotly_chart(fig2, use_container_width=True)

# Statistics
st.subheader("Statistics Summary")
col1, col2 = st.columns(2)

with col1:
    st.write("**Average Values**")
    avg_data = {
        'Parameter': ['pH', 'TDS', 'Turbidity', 'Dissolved Oxygen', 'Quality Score'],
        'Average': [
            f"{filtered_df['pH'].mean():.2f}",
            f"{filtered_df['TDS (mg/L)'].mean():.0f} mg/L",
            f"{filtered_df['Turbidity (NTU)'].mean():.2f} NTU",
            f"{filtered_df['Dissolved Oxygen (mg/L)'].mean():.2f} mg/L",
            f"{filtered_df['Quality Score'].mean():.0f}/100"
        ]
    }
    st.dataframe(pd.DataFrame(avg_data), hide_index=True, use_container_width=True)

with col2:
    st.write("**Data Quality Standards**")
    standards = {
        'Parameter': ['pH', 'TDS', 'Turbidity', 'Dissolved Oxygen'],
        'Acceptable Range': ['6.5 - 8.5', '< 500 mg/L', '< 5 NTU', '> 6 mg/L'],
        'Ideal': ['~7.5', '< 300 mg/L', '< 1 NTU', '> 7 mg/L']
    }
    st.dataframe(pd.DataFrame(standards), hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.caption("📊 Demo Data | Water quality parameters are synthetically generated for demonstration purposes")