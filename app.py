import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import calendar
import datetime
from pathlib import Path

DATE_COLUMN = 'acq_date'

st.title('Australia Bush Fires')
st.write('See the fires in Australia')

df = pd.read_csv(Path(
    './dataset/data.csv'), parse_dates=[DATE_COLUMN])

df = df.sort_values(by=DATE_COLUMN)
FIRST_DATE = df.loc[0, DATE_COLUMN]
DEFAULT_DATE = df.loc[df.shape[0] - 1, DATE_COLUMN]

months = { calendar.month_name[idx]: idx for idx in df[DATE_COLUMN].dt.month.unique() }

def get_min_max_days_from_month(data, month):
    days = data[data[DATE_COLUMN].dt.month == month][DATE_COLUMN].dt.day
    return int(days.iloc[0]), int(days.iloc[-1])
    

def get_year_from_month(data, month):
    years = data[data[DATE_COLUMN].dt.month == month][DATE_COLUMN].dt.year
    return int(years.iloc[0])

# date selection
month_name = st.selectbox('Select a month', list(months.keys()))
aggr_month = st.checkbox('Aggregate per month (it may take a while)')

if aggr_month:
    date = datetime.datetime(get_year_from_month(df, months[month_name]) , months[month_name], 1)
    data = df[df[DATE_COLUMN].dt.month == date.month]
    st.write(f"{data.shape[0]} fires on {date.strftime('%B %Y')}")
else:
    day = st.slider('Day',*get_min_max_days_from_month(df, months[month_name]))
    date = datetime.datetime(get_year_from_month(df, months[month_name]) , months[month_name], day)
    data = df[df[DATE_COLUMN] == date]
    st.write(f"{data.shape[0]} fires on {date.strftime('%A %B %Y')}")
# map

initial_view_state = pdk.ViewState(
    latitude=-26.14507,
    longitude=133.53627,
    zoom=4,
    pitch=30)


tooltip = {
    "html": "<b>Elevation:</b> {elevationValue} <br/>",
    "style": {
        "color": "white"
    }
}

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=initial_view_state,
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data,
            get_position='[longitude, latitude]',
            radius=10000,
            get_elevation='properties.brightness',
            elevation_scale=200,
            # elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=data,
            get_position='[longitude, latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=10000,
        ),
    ],
    tooltip=tooltip
))

month_data = df[df[DATE_COLUMN].dt.month ==date.month]
month_data = month_data.set_index(DATE_COLUMN, drop=True)

st.write(f'Fires per day in {month_name}')

st.bar_chart(month_data.groupby([month_data.index.day]).count().brightness)