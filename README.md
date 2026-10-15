
# NASA Asteroid Tracker ☄️

An interactive dashboard for exploring near-Earth asteroids using NASA's NeoWs API.

## Features

- Explore near-Earth objects by date
- View estimated diameter, distance, and velocity
- Filter potentially hazardous asteroids
- Interactive Plotly scatter plot
- Sortable data table and CSV export

## Requirements

- Python 3.10+
-  NASA API key

## Setup

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`.
5. Add your own NASA API key to `.env`.
6. Run the dashboard:

   ```bash
   streamlit run app.py
   ```

## Data source

NASA Near Earth Object Web Service (NeoWs):
https://api.nasa.gov/

The potentially hazardous classification does not mean an asteroid is predicted to hit Earth.
Diameter values are estimates.

## Author

Zahra Moslehi Jouybari
