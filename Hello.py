# ------------------------------------------------------------------------------------------------
# Import required libraries
# ------------------------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# ------------------------------------------------------------------------------------------------
# DATA LOADING AND PREPROCESSING
# ------------------------------------------------------------------------------------------------
# Define the path to the dataset
data_path = "data/integrated_water_related_data (1) (1).csv"

# Try to load the dataset or display an error message if the file is not found
try:
    data = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Failed to load data from {data_path}. Please check the file path and ensure the file exists.")
    st.stop()

# Manually adding coordinates for countries for demonstration.
country_coords = {
    'Australia': (-25.2744, 133.7751),
    'Belarus': (53.7098, 27.9534),
    'Belgium': (50.5039, 4.4699),
    'Bulgaria': (42.7339, 25.4858),
    'Costa Rica': (9.7489, -83.7534),
    'Croatia': (45.1, 15.2),
    'Czechia': (49.8175, 15.4730),
    'Denmark': (56.2639, 9.5018),
    'Estonia': (58.5953, 25.0136)
}

# Handle the case where 'Entity' might not be in the dataset
if 'Entity' in data.columns:
    data['latitude'] = data['Entity'].map(lambda x: country_coords.get(x, (None, None))[0])
    data['longitude'] = data['Entity'].map(lambda x: country_coords.get(x, (None, None))[1])
else:
    st.error("The expected 'Entity' column is not in the dataset.")
    st.stop()

# ------------------------------------------------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# ------------------------------------------------------------------------------------------------
st.set_page_config(page_title="Wastewater Impact Dashboard", layout="wide", page_icon=":recycle:", initial_sidebar_state="expanded")

# Page title and introduction
st.title('Wastewater Impact Dashboard')
st.markdown("""
This dashboard visualizes the impacts of wastewater discharges on both the environment and public health. It explores correlations and provides interactive data insights.
""")
# ------------------------------------------------------------------------------------------------
# OBJECTIVES SECTION
# ------------------------------------------------------------------------------------------------

st.header('Dashboard Objectives')
st.markdown("""
- **Evaluate Environmental Impacts**: Analyze how different levels and types of wastewater discharges affect environmental health, focusing on water quality, biodiversity, and ecosystem sustainability.
- **Assess Public Health Outcomes**: Investigate the correlation between wastewater management practices and public health metrics, particularly the incidence of waterborne diseases and overall community health.
- **Promote Sustainable Practices**: Highlight the effectiveness of various wastewater treatment technologies and management strategies, encouraging the adoption of best practices that enhance sustainability and efficiency.
- **Facilitate Policy Development**: Provide data-driven insights to support the formulation and implementation of policies aimed at improving wastewater management frameworks at local, national, and international levels.
- **improve Community Engagement**: Encourage active participation by providing interactive tools that allow users to see the direct impact of different wastewater management scenarios.
""")

# ------------------------------------------------------------------------------------------------
# INTERACTIVE SIDEBAR FOR FILTERING DATA
# ------------------------------------------------------------------------------------------------
st.sidebar.header('Filter Data')
try:
    year_range = st.sidebar.slider('Select Year Range', int(data['Year'].min()), int(data['Year'].max()), (2015, 2019))
    entity_filter = st.sidebar.multiselect('Select Country', options=list(data['Entity'].unique()), default=list(data['Entity'].unique()))
    health_impact_filter = st.sidebar.multiselect('Select Health Impact Type', options=list(data['Health_Impact'].unique()), default=list(data['Health_Impact'].unique()))
except Exception as e:
    st.sidebar.error("Error loading filters: " + str(e))
    st.stop()

# Apply filters to data
filtered_data = data[(data['Year'] >= year_range[0]) & (data['Year'] <= year_range[1]) & (data['Entity'].isin(entity_filter)) & (data['Health_Impact'].isin(health_impact_filter))]

# ------------------------------------------------------------------------------------------------
# VISUALIZATIONS AND DASHBOARD ELEMENTS
# ------------------------------------------------------------------------------------------------
# Map visualization
if not filtered_data.empty:
    view_state = pdk.ViewState(latitude=filtered_data['latitude'].mean(), longitude=filtered_data['longitude'].mean(), zoom=3)
    filtered_data['color'] = filtered_data['Health_Impact'].apply(lambda x: [255, 0, 0, 160] if x == 'High' else [0, 255, 0, 160])
    map_layer = pdk.Layer(
        'ScatterplotLayer',
        data=filtered_data,
        get_position='[longitude, latitude]',
        get_color='color',
        get_radius=50000,
        pickable=True
    )
    map_fig = pdk.Deck(layers=[map_layer], initial_view_state=view_state, map_style='mapbox://styles/mapbox/light-v9')
    st.pydeck_chart(map_fig)
else:
    st.error("No data available for the selected year range and filters.")

# ------------------------------------------------------------------------------------------------
# DETAILED IMPACT ANALYSIS SECTION
# ------------------------------------------------------------------------------------------------

st.subheader("Detailed Impact Analysis")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Health Impact Over Time")
    health_data = filtered_data.groupby('Year')['Premature_Death_Count'].sum().reset_index()
    fig = px.line(health_data, x='Year', y='Premature_Death_Count', title="Premature Death Count Over Time", markers=True)
    st.plotly_chart(fig)
    st.markdown("This graph demonstrates the trend of premature death counts over time, providing insights into the health impact of unsafe water sources.")

with col2:
    st.markdown("### Environmental Impact Over Time")
    env_data = filtered_data.groupby('Year')['Total discharges to Inland waters(million m3)'].sum().reset_index()
    fig = px.line(env_data, x='Year', y='Total discharges to Inland waters(million m3)', title="Discharges to Inland Waters Over Time", markers=True)
    st.plotly_chart(fig)
    st.markdown("This graph shows the trend of discharges to inland waters over time, indicating the volume of wastewater released into natural water bodies.")

# ------------------------------------------------------------------------------------------------
# PIE CHART FOR HEALTH IMPACT DISTRIBUTION
# ------------------------------------------------------------------------------------------------

pie_data = filtered_data['Health_Impact'].value_counts()

st.subheader("Health Impact Distribution")
pie_data = filtered_data['Health_Impact'].value_counts().reset_index()
pie_data.columns = ['Health_Impact', 'Count']
fig = px.pie(pie_data, values='Count', names='Health_Impact', title="Health Impact Distribution")
st.plotly_chart(fig)

st.markdown("This pie chart displays the distribution of health impacts, categorizing them by severity to aid in prioritizing health interventions.")

# ------------------------------------------------------------------------------------------------
# ADDITIONAL INFORMATION AND RECOMMENDATIONS
# ------------------------------------------------------------------------------------------------

st.markdown("---")
st.markdown("""
### Additional Information

## Importance of Wastewater Management
The management of wastewater is crucial not only for maintaining environmental integrity but also for safeguarding public health. Effective wastewater treatment systems help mitigate the adverse effects of pollutants on both ecosystems and human communities. Wastewater management involves various processes to treat water from industrial, residential, and other sources before it is released back into the environment. Properly treated wastewater prevents the spread of diseases, protects wildlife, and keeps water bodies clean for recreational and other uses.

## Environmental and Socio-Economic Impacts
Untreated or poorly treated wastewater can have devastating impacts on the environment and public health. Pollutants in wastewater can degrade water quality, leading to eutrophication, which decreases the oxygen level in water bodies and destroys aquatic life. On a socio-economic level, poor water quality affects agriculture, fisheries, tourism, and can cause health crises that strain healthcare systems and hinder economic development.

## Challenges and Opportunities
One of the main challenges in wastewater management is the aging infrastructure that cannot cope with the increasing population and urbanization. Additionally, many regions lack the financial resources and technical expertise to implement modern wastewater treatment solutions. However, advancements in technology provide new opportunities for improving wastewater treatment processes and integrating sustainable practices such as water recycling and energy recovery from waste.

## Policy and Community Engagement
To address these challenges, it is essential to establish strong policies that enforce stringent wastewater treatment standards and encourage investments in infrastructure upgrades. Community engagement is also critical; educating the public about the importance of water conservation and pollution prevention can lead to more sustainable water use practices.

## Global Cooperation
Wastewater management is a global issue that requires cooperation across borders. By sharing technologies, best practices, and financial resources, countries can enhance their capabilities to manage wastewater effectively and protect our global water resources for future generations.

By understanding the sources, types, effects, and mitigation strategies for water contaminants, stakeholders can work towards protecting water resources and promoting sustainable water management strategies
.]
""")

st.markdown("### Recommendations for Improvement")
st.markdown("""
The following recommendations are derived from an analysis of the data, aiming to address critical areas for improving wastewater management and enhancing public health and environmental integrity:

1. **Enhance Monitoring Systems**: 
   - **Objective**: Strengthen monitoring to quickly identify and address sources of pollution.
   - **Action**: Implement advanced sensor technologies and real-time data processing tools to monitor wastewater quality continuously. This enables early detection of anomalies that may indicate pollution events, allowing for immediate response and mitigation.

2. **Infrastructure Upgrades**: 
   - **Objective**: Invest in modernizing wastewater treatment facilities to increase capacity and improve treatment efficiency.
   - **Action**: Allocate funding for upgrading aging infrastructure and incorporate advanced treatment technologies such as membrane bioreactors and tertiary treatment processes. These upgrades will enhance the ability to remove contaminants and meet or exceed regulatory standards.

3. **Public Awareness Campaigns**: 
   - **Objective**: Educate the public on the impacts of wastewater on ecosystems and public health, promoting responsible behavior.
   - **Action**: Develop and implement comprehensive educational programs and community outreach initiatives. These should focus on the importance of reducing pollutant loads from household and industrial sources, proper disposal of hazardous materials, and the benefits of reduced water pollution.

4. **Regulatory Compliance**: 
   - **Objective**: Ensure strict compliance with environmental regulations to mitigate the negative impacts of wastewater discharges.
   - **Action**: Strengthen enforcement mechanisms by equipping regulatory bodies with the necessary tools and authority to monitor compliance and penalize non-compliance. Regularly update regulations to reflect advances in wastewater treatment technology and emerging pollutants of concern.

5. **Community Engagement**: 
   - **Objective**: Foster community involvement in wastewater management to encourage sustainable practices and local stewardship.
   - **Action**: Create platforms for community engagement and decision-making in water management policies. This includes forming watershed committees, hosting public forums, and involving local communities in the planning and operation of local water treatment facilities.

Implementing these recommendations requires a coordinated effort among government agencies, industry stakeholders, and the public. By addressing these key areas, significant strides can be made toward sustainable water management and enhanced protection of both public health and the environment.
""")

# ------------------------------------------------------------------------------------------------
# INTERACTIVE DATA EXPLORATIONS SECTION
# ------------------------------------------------------------------------------------------------

# Button to refresh the dashboard based on user interaction
if st.button("Refresh Dashboard"):
    st.experimental_rerun()
