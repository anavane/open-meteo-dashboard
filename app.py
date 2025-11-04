# app.py
import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import pandas as pd

st.set_page_config(page_title="Open-Meteo Interactive Weather Dashboard", page_icon="🌦️", layout="centered")
st.title("🌦️ Open-Meteo Interactive Weather Dashboard")
st.write("Click a point on the map to fetch hourly and daily weather from the Open-Meteo API.")

st.subheader("1️⃣ Select location (click on the map)")
m = folium.Map(location=[35.0, 135.0], zoom_start=5)  # centered on East Asia/Japan
map_data = st_folium(m, height=450, width=900)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.success(f"Selected location: latitude {lat:.4f}, longitude {lon:.4f}")

    # Build Open-Meteo request
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,weathercode,windspeed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        st.error(f"Failed to fetch weather data: {e}")
        st.stop()

    # Daily summary table
    st.subheader("📅 Daily summary")
    if "daily" in data:
        daily = data["daily"]
        df_daily = pd.DataFrame({
            "date": daily.get("time", []),
            "temp_max (°C)": daily.get("temperature_2m_max", []),
            "temp_min (°C)": daily.get("temperature_2m_min", []),
            "precipitation (mm)": daily.get("precipitation_sum", []),
        })
        st.dataframe(df_daily)
    else:
        st.write("No daily data available.")

    # Hourly temperature chart
    st.subheader("🌡️ Hourly temperature")
    if "hourly" in data:
        hourly = data["hourly"]
        df_hourly = pd.DataFrame({
            "time": hourly.get("time", []),
            "temperature_2m": hourly.get("temperature_2m", []),
            "precipitation": hourly.get("precipitation", []),
            "windspeed_10m": hourly.get("windspeed_10m", []),
        })
        # convert time to index for plotting
        if not df_hourly.empty:
            df_hourly["time"] = pd.to_datetime(df_hourly["time"])
            df_hourly = df_hourly.set_index("time")
            st.line_chart(df_hourly[["temperature_2m"]])
            st.line_chart(df_hourly[["precipitation"]])
            st.line_chart(df_hourly[["windspeed_10m"]])
        else:
            st.write("No hourly data available.")
    else:
        st.write("No hourly data available.")

    # Raw JSON expandable
    with st.expander("Show full API response (JSON)"):
        st.json(data)

else:
    st.info("Click a point on the map to fetch weather data for that location.")
