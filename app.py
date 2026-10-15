import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()
KEY = os.getenv("NASA_API_KEY")
URL = "https://api.nasa.gov/neo/rest/v1/feed"

st.set_page_config(
    page_title="NASA Asteroid Tracker",
    page_icon="☄️",
    layout="wide"
)

st.title("☄️ NASA Asteroid Tracker")
st.caption("Explore near-Earth asteroids using NASA's NeoWs API")

if not KEY:
    st.error("NASA_API_KEY پیدا نشد. فایل .env را بررسی کن.")
    st.stop()

# Date selection
today = date.today()
start_date = st.date_input("Start date", today)
end_date = st.date_input(
    "End date",
    min(today + timedelta(days=1), today + timedelta(days=7))
)

if start_date > end_date:
    st.error("تاریخ شروع باید قبل از تاریخ پایان باشد.")
    st.stop()

if (end_date - start_date).days > 6:
    st.error("هر درخواست ناسا حداکثر بازه ۷ روزه را می‌پذیرد.")
    st.stop()

@st.cache_data(ttl=3600)
def get_asteroids(start, end):
    response = requests.get(
        URL,
        params={
            "start_date": start,
            "end_date": end,
            "api_key": KEY
        },
        timeout=30
    )
    response.raise_for_status()

    rows = []
    data = response.json()["near_earth_objects"]

    for day, objects in data.items():
        for obj in objects:
            diameter = obj["estimated_diameter"]["meters"]
            approach = obj["close_approach_data"][0]

            rows.append({
                "Name": obj["name"],
                "Date": day,
                "Min diameter (m)": diameter["estimated_diameter_min"],
                "Max diameter (m)": diameter["estimated_diameter_max"],
                "Miss distance (km)": float(
                    approach["miss_distance"]["kilometers"]
                ),
                "Speed (km/h)": float(
                    approach["relative_velocity"]["kilometers_per_hour"]
                ),
                "Lunar distances": float(
                    approach["miss_distance"]["kilometers"]
                ) / 384400,
                "Potentially hazardous": obj[
                    "is_potentially_hazardous_asteroid"
                ]
            })

    return pd.DataFrame(rows)

if st.button("Load asteroids", type="primary"):
    st.session_state["asteroid_dates"] = (
        start_date.isoformat(),
        end_date.isoformat()
    )

if "asteroid_dates" in st.session_state:
    saved_start, saved_end = st.session_state["asteroid_dates"]

    try:
        with st.spinner("Loading asteroid data from NASA..."):
            df = get_asteroids(saved_start, saved_end)

        if df.empty:
            st.warning("No asteroids found for this date range.")
            st.stop()

        hazardous_only = st.toggle(
            "Show potentially hazardous asteroids only",
            value=False
        )

        view = df.copy()
        if hazardous_only:
            view = view[view["Potentially hazardous"]]

        col1, col2, col3 = st.columns(3)
        col1.metric("Asteroids", len(view))
        col2.metric(
            "Potentially hazardous",
            int(view["Potentially hazardous"].sum())
        )
        col3.metric(
            "Largest estimated diameter",
            f'{view["Max diameter (m)"].max():,.0f} m'
        )

        st.subheader("Asteroid distance vs. size")

        fig = px.scatter(
            view,
            x="Miss distance (km)",
            y="Max diameter (m)",
            color="Potentially hazardous",
            hover_name="Name",
            hover_data=["Date", "Speed (km/h)", "Lunar distances"],
            log_x=True,
            title="How far away are the asteroids?"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Asteroid table")

        sorted_view = view.sort_values(
            "Max diameter (m)", ascending=False
        )
        st.dataframe(sorted_view, use_container_width=True)

        csv = sorted_view.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="asteroid_tracker.csv",
            mime="text/csv"
        )

        st.caption(
            "NASA's potentially hazardous classification is not a prediction "
            "that an asteroid will hit Earth. Diameter values are estimates."
        )

    except requests.RequestException as error:
        st.error(f"NASA API request failed: {error}")
    except (KeyError, ValueError, TypeError) as error:
        st.error(f"Could not process NASA's response: {error}")
