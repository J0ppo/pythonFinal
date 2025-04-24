import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
from PIL import Image
# import seaborn as sns

def difference(a, b):
    return abs(a - b)

def cityBarChart(city, data):
    # Turn dict into two lists
    labels = list(data.keys())
    values = list(data.values())

    # Plot
    fig, ax = plt.subplots()
    ax.bar(labels, values, color='mediumseagreen')

    # Customize labels
    ax.set_xlabel("Pollutant Type")
    ax.set_ylabel("AQI Value")
    ax.set_title(f"Air Quality Index by Pollutant in {city}")
    plt.xticks(rotation=45)  # Rotate x-labels for readability



# [DA1] Got rid of lat/long duplicates and value duplicates (there were quite a lot of same city, same country,
# and same air quality values with different lat/long), and changed NaNs to unknown
dfOG = pd.read_csv('AirQuality.csv')
dfClean = dfOG.drop_duplicates(subset = ['lat','lng'], keep = 'first')
dfClean = dfClean.drop_duplicates(subset = ['Country', 'City', 'AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value'])
dfClean['AQI Value'] = pd.to_numeric(dfClean['AQI Value'], errors= 'coerce')
dfClean = dfClean[(dfClean['AQI Value'] > 0) & (dfClean['AQI Value'] <= 500)]
dfClean['lng'] = pd.to_numeric(dfClean['lng'], errors= "coerce")
dfClean['lat'] = pd.to_numeric(dfClean['lat'], errors= "coerce")
dfClean['Country'] = dfClean['Country'].apply(lambda x: 'Unknown' if pd.isna(x) else x)

# [ST4]
img = Image.open("aqaw_2021_0.png")
st.image(img, width= 350)
st.title("Air Quality Map")
st.write("Let's look at some air quality data around the world!")

# [ST1]
countryChoice = st.sidebar.selectbox("Choose a country:", dfClean['Country'].unique())
filtered_df = dfClean[dfClean['Country'] == countryChoice]

# [Map]
st.map(data = filtered_df, latitude = 'lat', longitude = 'lng', zoom = 4)



cityChoice1 = st.sidebar.selectbox("Type the city that you'd like to see the data for"
                                   , dfClean['City'])
cityRow = dfClean[dfClean['City'] == cityChoice1]
pollutants = {
    'Overall AQI': cityRow['AQI Value'].values[0],
    'Ozone AQI': cityRow['Ozone AQI Value'].values[0],
    'NO2 AQI': cityRow['NO2 AQI Value'].values[0],
    'PM2.5 AQI': cityRow['PM2.5 AQI Value'].values[0]
}

st.pyplot(cityBarChart(cityChoice1, pollutants))



st.write(dfClean.head(10))
# Create heatmap layer
heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=dfClean,
    get_position=['lng', 'lat'],
    get_weight="AQI Value",
    radius_pixels=40
)


# Set the initial view
view_state = pdk.ViewState(
    latitude=filtered_df['lat'].mean(),
    longitude=filtered_df['lng'].mean(),
    zoom=3,
    pitch=0
)

st.pydeck_chart(pdk.Deck(
    layers=[heatmap_layer],
    initial_view_state=view_state,
#    tooltip={"text": "AQI: {'AQI Value'}"}
))