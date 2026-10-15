import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["NASA_API_KEY"]

URL = "https://api.nasa.gov/neo/rest/v1/feed"


def get_week(start, end):
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

    for date, objects in response.json()["near_earth_objects"].items():
        for asteroid in objects:
            diameter = asteroid["estimated_diameter"]["meters"]
            approach = asteroid["close_approach_data"][0]

            rows.append({
                "name": asteroid["name"],
                "date": date,
                "diameter_min_m": diameter["estimated_diameter_min"],
                "diameter_max_m": diameter["estimated_diameter_max"],
                "miss_km": float(
                    approach["miss_distance"]["kilometers"]
                ),
                "speed_kmh": float(
                    approach["relative_velocity"]["kilometers_per_hour"]
                ),
                "hazardous": asteroid[
                    "is_potentially_hazardous_asteroid"
                ]
            })

    return pd.DataFrame(rows)


try:
    df = get_week("2026-10-12", "2026-10-18")

    df["lunar_distances"] = df["miss_km"] / 384400

    print("\nTotal asteroids:", len(df))
    print("\nTop 10 largest asteroids:")
    print(
        df.sort_values("diameter_max_m", ascending=False)
        .head(10)
        .to_string(index=False)
    )

except requests.RequestException as error:
    print("NASA API error:", error)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

colors = df["hazardous"].map({
    True: "red",
    False: "blue"
})

plt.scatter(
    df["miss_km"] / 1_000_000,
    df["diameter_max_m"],
    c=colors,
    alpha=0.7
)

plt.xlabel("Distance from Earth (million km)")
plt.ylabel("Maximum Estimated Diameter (m)")
plt.title("Near-Earth Asteroids Tracker")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
