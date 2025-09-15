import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from collections import Counter
import datetime

# Page configuration
st.set_page_config(
    page_title="Electric Vehicle Analytics Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e1e5eb;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and Description
st.markdown('<h1 class="main-header">⚡ Electric Vehicle Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Comprehensive analysis of electric vehicle registrations and market trends**")

# Data loading function
@st.cache_data
def load_data():
    """Load and cache the electric vehicle dataset"""
    # Replace with your actual data loading method
    # For demo purposes, creating sample data structure
    path = r'C:\Users\Admin\Desktop\Desney\Projects\Electric_vehicles_analysis\Electric_Vehicle_Population_Data.csv'

    df = pd.read_csv(path)
    return df
    
    # Remove this section and uncomment above when you have your actual data
    st.warning("⚠️ Please update the load_data() function with your actual CSV file path")
    return None

# Load data
df = load_data()

# Sidebar for filters and controls
st.sidebar.header("🎛️ Dashboard Controls")

if df is not None:
    # Filters
    st.sidebar.subheader("Filters")
    
    # Year filter
    min_year, max_year = int(df['Model Year'].min()), int(df['Model Year'].max())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    
    # State filter
    selected_states = st.sidebar.multiselect(
        "Select States",
        options=sorted(df['State'].unique()),
        default=sorted(df['State'].unique())[:5]  # Default to top 5 states
    )
    
    # Make filter
    selected_makes = st.sidebar.multiselect(
        "Select Vehicle Makes",
        options=sorted(df['Make'].unique()),
        default=df['Make'].value_counts().head(10).index.tolist()
    )
    
    # EV Type filter
    selected_ev_types = st.sidebar.multiselect(
        "Select EV Types",
        options=df['Electric Vehicle Type'].unique(),
        default=df['Electric Vehicle Type'].unique()
    )
    
    # Apply filters
    filtered_df = df[
        (df['Model Year'].between(year_range[0], year_range[1])) &
        (df['State'].isin(selected_states)) &
        (df['Make'].isin(selected_makes)) &
        (df['Electric Vehicle Type'].isin(selected_ev_types))
    ]
    
    # Main dashboard
    if len(filtered_df) > 0:
        # Key Metrics Row
        st.header("📊 Key Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="Total Vehicles",
                value=f"{len(filtered_df):,}",
                delta=f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
            )
        
        with col2:
            st.metric(
                label="Unique Makes",
                value=filtered_df['Make'].nunique()
            )
        
        with col3:
            st.metric(
                label="Unique Models",
                value=filtered_df['Model'].nunique()
            )
        
        with col4:
            avg_range = filtered_df[filtered_df['Electric Range'] > 0]['Electric Range'].mean()
            st.metric(
                label="Avg Range (miles)",
                value=f"{avg_range:.0f}" if not pd.isna(avg_range) else "N/A"
            )
        
        with col5:
            st.metric(
                label="States Covered",
                value=filtered_df['State'].nunique()
            )
        
        # Visualization Tabs
        st.header("📈 Interactive Visualizations")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🏭 Market Analysis", 
            "📅 Time Trends", 
            "🗺️ Geographic", 
            "🔋 Range Analysis", 
            "💰 Pricing", 
            "🏆 Rankings"
        ])
        
        with tab1:
            st.subheader("Market Share Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Market share pie chart
                make_counts = filtered_df['Make'].value_counts().head(15)
                fig_pie = px.pie(
                    values=make_counts.values,
                    names=make_counts.index,
                    title="Top 15 Makes - Market Share"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # EV Type distribution
                ev_type_counts = filtered_df['Electric Vehicle Type'].value_counts()
                fig_ev_type = px.bar(
                    x=ev_type_counts.index,
                    y=ev_type_counts.values,
                    title="Electric Vehicle Type Distribution",
                    labels={'x': 'Vehicle Type', 'y': 'Count'}
                )
                st.plotly_chart(fig_ev_type, use_container_width=True)
            
            # Market concentration
            st.subheader("Market Concentration")
            top_10_makes = make_counts.head(10)
            fig_concentration = px.treemap(
                names=top_10_makes.index,
                values=top_10_makes.values,
                title="Market Concentration - Top 10 Makes"
            )
            st.plotly_chart(fig_concentration, use_container_width=True)
        
        with tab2:
            st.subheader("Temporal Trends")
            
            # Yearly trend
            yearly_counts = filtered_df.groupby('Model Year').size().reset_index()
            yearly_counts.columns = ['Year', 'Count']
            
            fig_trend = px.line(
                yearly_counts,
                x='Year',
                y='Count',
                title="Electric Vehicle Registration Trend",
                markers=True
            )
            fig_trend.update_layout(hovermode='x')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Growth rate analysis
            if len(yearly_counts) > 1:
                yearly_counts['Growth_Rate'] = yearly_counts['Count'].pct_change() * 100
                fig_growth = px.bar(
                    yearly_counts[1:],  # Skip first year (no growth rate)
                    x='Year',
                    y='Growth_Rate',
                    title="Year-over-Year Growth Rate (%)"
                )
                st.plotly_chart(fig_growth, use_container_width=True)
            
            # Seasonal analysis by make
            st.subheader("Top Makes Over Time")
            top_makes = filtered_df['Make'].value_counts().head(5).index
            yearly_make_data = filtered_df[filtered_df['Make'].isin(top_makes)].groupby(['Model Year', 'Make']).size().reset_index()
            yearly_make_data.columns = ['Year', 'Make', 'Count']
            
            fig_make_trend = px.line(
                yearly_make_data,
                x='Year',
                y='Count',
                color='Make',
                title="Registration Trends by Top Makes"
            )
            st.plotly_chart(fig_make_trend, use_container_width=True)
        
        with tab3:
            st.subheader("Geographic Distribution")
            
            # State-wise distribution
            state_counts = filtered_df['State'].value_counts().reset_index()
            state_counts.columns = ['State', 'Count']
            
            # Choropleth map
            fig_map = px.choropleth(
                state_counts,
                locations='State',
                color='Count',
                locationmode='USA-states',
                title='Electric Vehicle Distribution Across States',
                color_continuous_scale='Blues'
            )
            fig_map.update_layout(geo_scope="usa")
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Top cities analysis
            if 'City' in filtered_df.columns:
                st.subheader("Top Cities")
                city_counts = filtered_df['City'].value_counts().head(20)
                fig_cities = px.bar(
                    x=city_counts.values,
                    y=city_counts.index,
                    orientation='h',
                    title="Top 20 Cities by EV Count"
                )
                fig_cities.update_layout(height=600)
                st.plotly_chart(fig_cities, use_container_width=True)
        
        with tab4:
            st.subheader("Electric Range Analysis")
            
            if 'Electric Range' in filtered_df.columns:
                range_data = filtered_df[filtered_df['Electric Range'] > 0]
                
                if len(range_data) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Range distribution
                        fig_hist = px.histogram(
                            range_data,
                            x='Electric Range',
                            nbins=30,
                            title="Electric Range Distribution"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col2:
                        # Range by vehicle type
                        fig_box = px.box(
                            range_data,
                            x='Electric Vehicle Type',
                            y='Electric Range',
                            title="Range Distribution by Vehicle Type"
                        )
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    # Range by top makes
                    top_makes_range = filtered_df['Make'].value_counts().head(10).index
                    range_by_make = range_data[range_data['Make'].isin(top_makes_range)]
                    
                    fig_range_make = px.violin(
                        range_by_make,
                        x='Make',
                        y='Electric Range',
                        title="Electric Range Distribution by Top Makes"
                    )
                    fig_range_make.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_range_make, use_container_width=True)
                else:
                    st.warning("No range data available for the selected filters.")
            else:
                st.warning("Electric Range column not found in the dataset.")
        
        with tab5:
            st.subheader("Pricing Analysis")
            
            if 'Base MSRP' in filtered_df.columns:
                price_data = filtered_df[filtered_df['Base MSRP'] > 0]
                
                if len(price_data) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Price distribution
                        fig_price_hist = px.histogram(
                            price_data,
                            x='Base MSRP',
                            nbins=30,
                            title="Base MSRP Distribution"
                        )
                        st.plotly_chart(fig_price_hist, use_container_width=True)
                    
                    with col2:
                        # Average price by make
                        avg_price_by_make = price_data.groupby('Make')['Base MSRP'].mean().sort_values(ascending=False).head(15)
                        fig_avg_price = px.bar(
                            x=avg_price_by_make.values,
                            y=avg_price_by_make.index,
                            orientation='h',
                            title="Average MSRP by Make (Top 15)"
                        )
                        st.plotly_chart(fig_avg_price, use_container_width=True)
                    
                    # Price vs Range scatter
                    if 'Electric Range' in filtered_df.columns:
                        price_range_data = price_data[price_data['Electric Range'] > 0]
                        if len(price_range_data) > 0:
                            fig_scatter = px.scatter(
                                price_range_data,
                                x='Electric Range',
                                y='Base MSRP',
                                color='Make',
                                title="Price vs Range Analysis",
                                hover_data=['Model']
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.warning("No pricing data available for the selected filters.")
            else:
                st.warning("Base MSRP column not found in the dataset.")
        
        with tab6:
            st.subheader("Rankings and Comparisons")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top models
                st.write("**Top 15 Models**")
                model_counts = filtered_df.groupby(['Make', 'Model']).size().sort_values(ascending=False).head(15)
                model_df = model_counts.reset_index()
                model_df.columns = ['Make', 'Model', 'Count']
                model_df['Make_Model'] = model_df['Make'] + ' ' + model_df['Model']
                
                fig_models = px.bar(
                    model_df,
                    x='Count',
                    y='Make_Model',
                    orientation='h',
                    title="Top 15 Models by Registration Count"
                )
                fig_models.update_layout(height=500)
                st.plotly_chart(fig_models, use_container_width=True)
            
            with col2:
                # CAFV Eligibility
                st.write("**CAFV Eligibility Status**")
                cafv_counts = filtered_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].value_counts()
                fig_cafv = px.pie(
                    values=cafv_counts.values,
                    names=cafv_counts.index,
                    title="CAFV Eligibility Distribution"
                )
                st.plotly_chart(fig_cafv, use_container_width=True)
        
        # Data Table Section
        st.header("📋 Data Explorer")
        with st.expander("View Filtered Data"):
            st.write(f"Showing {len(filtered_df):,} records")
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name=f"filtered_ev_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Insights Section
        st.header("💡 Key Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            top_make = filtered_df['Make'].value_counts().index[0]
            top_make_count = filtered_df['Make'].value_counts().iloc[0]
            top_make_pct = (top_make_count / len(filtered_df)) * 100
            st.write(f"**Market Leader:** {top_make} dominates with {top_make_count:,} vehicles ({top_make_pct:.1f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if 'Electric Range' in filtered_df.columns:
                avg_range = filtered_df[filtered_df['Electric Range'] > 0]['Electric Range'].mean()
                if not pd.isna(avg_range):
                    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                    st.write(f"**Average Range:** {avg_range:.0f} miles per charge")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with insights_col2:
            most_common_type = filtered_df['Electric Vehicle Type'].value_counts().index[0]
            type_pct = (filtered_df['Electric Vehicle Type'].value_counts().iloc[0] / len(filtered_df)) * 100
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.write(f"**Vehicle Preference:** {most_common_type} represents {type_pct:.1f}% of all EVs")
            st.markdown('</div>', unsafe_allow_html=True)
            
            top_state = filtered_df['State'].value_counts().index[0]
            state_count = filtered_df['State'].value_counts().iloc[0]
            state_pct = (state_count / len(filtered_df)) * 100
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.write(f"**Geographic Leader:** {top_state} leads with {state_count:,} vehicles ({state_pct:.1f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.warning("No data matches the selected filters. Please adjust your filter criteria.")

else:
    # Demo mode or data loading instructions
    st.error("❌ Data not loaded. Please update the `load_data()` function with your CSV file path.")
    
    st.markdown("## 📁 Setup Instructions")
    st.markdown("""
    To use this dashboard with your electric vehicle data:
    
    1. **Update the `load_data()` function** in the code:
       ```python
       @st.cache_data
       def load_data():
           df = pd.read_csv('path_to_your_ev_data.csv')
           return df
       ```
    
    2. **Ensure your CSV has these columns:**
       - VIN (1-10)
       - County
       - City
       - State
       - Postal Code
       - Model Year
       - Make
       - Model
       - Electric Vehicle Type
       - Clean Alternative Fuel Vehicle (CAFV) Eligibility
       - Electric Range
       - Base MSRP
       - Legislative District
       - DOL Vehicle ID
       - Vehicle Location
       - Electric Utility
       - 2020 Census Tract
    
    3. **Run the app:**
       ```bash
       streamlit run app.py
       ```
    """)
    
    # Sample data structure for demonstration
    st.markdown("## 📊 Expected Data Structure")
    sample_data = {
        'VIN (1-10)': ['1HGBH41JX', '2T3ZFREV4', '5YJ3E1EA3'],
        'County': ['King', 'Snohomish', 'Pierce'],
        'City': ['Seattle', 'Bellevue', 'Tacoma'],
        'State': ['WA', 'WA', 'WA'],
        'Model Year': [2023, 2022, 2023],
        'Make': ['TESLA', 'NISSAN', 'FORD'],
        'Model': ['MODEL 3', 'LEAF', 'MUSTANG MACH-E'],
        'Electric Vehicle Type': ['Battery Electric Vehicle (BEV)', 'Battery Electric Vehicle (BEV)', 'Battery Electric Vehicle (BEV)'],
        'Electric Range': [272, 149, 312],
        'Base MSRP': [46440, 31620, 50400]
    }
    
    sample_df = pd.DataFrame(sample_data)
    st.dataframe(sample_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**📊 Electric Vehicle Analytics Dashboard** | Built with Streamlit & Plotly | Data Analysis & Visualization")

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("""
This dashboard provides comprehensive analysis of electric vehicle registration data including:

- **Market Analysis:** Brand dominance and vehicle type distribution
- **Temporal Trends:** Growth patterns over time
- **Geographic Distribution:** State and city-wise adoption
- **Range Analysis:** Electric range capabilities
- **Pricing Insights:** MSRP analysis and trends
- **Rankings:** Top models and comparisons

**Features:**
- Interactive filtering
- Real-time visualizations
- Data export capabilities
- Responsive design
""")

st.sidebar.markdown("### 🎯 Filters Applied")
if df is not None:
    st.sidebar.write(f"📅 Years: {year_range[0]} - {year_range[1]}")
    st.sidebar.write(f"🏛️ States: {len(selected_states)}")
    st.sidebar.write(f"🚗 Makes: {len(selected_makes)}")
    st.sidebar.write(f"⚡ EV Types: {len(selected_ev_types)}")

# Performance metrics in sidebar
if df is not None and len(filtered_df) > 0:
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Total Records", f"{len(filtered_df):,}")
    st.sidebar.metric("Unique Makes", f"{filtered_df['Make'].nunique()}")
    st.sidebar.metric("Year Span", f"{filtered_df['Model Year'].max() - filtered_df['Model Year'].min() + 1} years")

# Advanced settings
with st.sidebar.expander("⚙️ Advanced Settings"):
    st.write("**Chart Themes**")
    chart_theme = st.selectbox("Select Theme", ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"])
    
    st.write("**Display Options**")
    show_data_labels = st.checkbox("Show Data Labels", value=True)
    animation_enabled = st.checkbox("Enable Animations", value=True)

# Apply advanced settings globally for plotly
if 'chart_theme' in locals():
    import plotly.io as pio
    pio.templates.default = chart_theme