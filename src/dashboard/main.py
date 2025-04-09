import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import calendar
from datetime import datetime
from streamlit_calendar import calendar
import sys; sys.path.append(str(__file__).rsplit("src", 1)[0] + "src")

from api.openrouteservice_client import get_route
from dashboard.inventory import render_inventory_editor
from dashboard.quick_actions import render_quick_actions
from dashboard.analytics import render_analytics_summary
from route_history import render_route_history


def render_inventory_trends():
    st.subheader("📈 Inventory Trends (Simulated)")
    dates = pd.date_range(end=pd.Timestamp.today(), periods=10)
    data = {
        "Laptops": np.random.randint(5, 15, size=10),
        "Monitors": np.random.randint(1, 6, size=10),
        "Printers": np.random.randint(0, 3, size=10),
        "Cables": np.random.randint(20, 30, size=10),
    }
    trends_df = pd.DataFrame(data, index=dates)
    st.line_chart(trends_df)


def render_dashboard_overview():
    st.subheader("📊 Dashboard Overview")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Total Routes Planned", value="24", delta="+3 today")
    kpi2.metric(label="Deliveries Completed", value="19", delta="+5%")
    kpi3.metric(label="Avg. Emissions per Route", value="4.8 kg", delta="-0.3 kg")
    st.markdown("---")
    st.markdown("### 🔎 Summary")
    st.write("""
        - Your fleet planning is improving with higher delivery completion.
        - Emissions per route are reducing, indicating better optimization.
        - You’ve planned more routes today than yesterday—keep it up!
    """)


def calculate_emissions(distance_km: float, vehicle_type: str) -> float:
    factors = {"Petrol": 0.192, "Diesel": 0.171, "Electric": 0.05}
    if vehicle_type not in factors:
        raise ValueError(f"Invalid vehicle type: {vehicle_type}")
    return distance_km * factors[vehicle_type]


st.set_page_config(page_title="PathX Route Planner", page_icon="🗺️", layout="wide")

st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

if 'map_center' not in st.session_state:
    st.session_state.map_center = [49.41461, 8.681495]
if 'route_points' not in st.session_state:
    st.session_state.route_points = [[49.41461, 8.681495], [49.420318, 8.687872]]
if 'route_info' not in st.session_state:
    st.session_state.route_info = {'distance': 0, 'duration': 0, 'emissions': 0}

st.title("🗺️ PathX Route Planner")

with st.sidebar:
    st.header("Route Parameters")
    st.subheader("Coordinates")
    start_coords = st.text_input("Start (lat, lon)", "49.41461, 8.681495")
    end_coords = st.text_input("End (lat, lon)", "49.420318, 8.687872")
    st.subheader("Vehicle Type")
    vehicle_type = st.selectbox("Select Vehicle Type", ["Petrol", "Diesel", "Electric"])
    st.markdown("---")
    get_route_btn = st.button("Get Route", type="primary")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Route Map")
    try:
        if get_route_btn:
            route_calculated = False
            try:
                start_lat, start_lon = map(float, start_coords.split(','))
                end_lat, end_lon = map(float, end_coords.split(','))

                if not (-90 <= start_lat <= 90 and -180 <= start_lon <= 180):
                    raise ValueError("Invalid start coordinates")
                if not (-90 <= end_lat <= 90 and -180 <= end_lon <= 180):
                    raise ValueError("Invalid end coordinates")

                coords = [(start_lon, start_lat), (end_lon, end_lat)]
                route_info = get_route(coords)
                route_coords = [(lat, lon) for lon, lat in route_info['geometry']]
                st.session_state.map_center = [(start_lat + end_lat) / 2, (start_lon + end_lon) / 2]
                st.session_state.route_points = route_coords
                st.session_state.route_info = {
                    'distance': route_info['distance'] / 1000,
                    'duration': route_info['duration'] / 3600,
                    'emissions': calculate_emissions(route_info['distance'] / 1000, vehicle_type)
                }
                route_calculated = True

            except ValueError as e:
                st.error(f"Error parsing coordinates: {str(e)}")
            except Exception as e:
                msg = str(e)
                if "Could not find routable point" in msg:
                    st.error("No route found. Try different locations.")
                else:
                    st.error(f"Error: {msg}")

            if not route_calculated:
                st.session_state.map_center = [49.41461, 8.681495]
                st.session_state.route_points = [[49.41461, 8.681495], [49.420318, 8.687872]]

        m = folium.Map(location=st.session_state.map_center, zoom_start=13, tiles='OpenStreetMap')
        folium.Marker(st.session_state.route_points[0], popup='Start', icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(st.session_state.route_points[-1], popup='End', icon=folium.Icon(color='red')).add_to(m)
        folium.PolyLine(st.session_state.route_points, color='blue', weight=5).add_to(m)
        st_folium(m, width=700, height=500)

        render_dashboard_overview()
        st.markdown("---")
        render_inventory_editor()
        with st.expander("Show Inventory Trends"):
            render_inventory_trends()

        st.subheader("Selected Coordinates")
        st.dataframe(pd.DataFrame({
            "Location": ["Start", "End"],
            "Coordinates": [start_coords, end_coords]
        }), hide_index=True)

        st.subheader("📅 Delivery Calendar")
        calendar_options = {
            "initialView": "dayGridMonth",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "height": 500,
            "editable": False,
            "selectable": True,
            "dayMaxEvents": True,
        }
        calendar_events = [
            {"title": "📦 Delivery - Laptops", "start": f"{datetime.today().strftime('%Y-%m')}-10"},
            {"title": "📦 Delivery - Monitors", "start": f"{datetime.today().strftime('%Y-%m')}-15"},
            {"title": "🔄 Inventory Sync", "start": f"{datetime.today().strftime('%Y-%m')}-20"},
        ]
        result = calendar(events=calendar_events, options=calendar_options)
        if result and result.get("dateClick"):
            st.info(f"You clicked on {result['dateClick']['date']}")

    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")

with col2:
    st.subheader("Route Information")
    if st.session_state.route_info['distance'] > 0:
        st.success("Route calculated successfully!")
        st.metric("Total Distance", f"{st.session_state.route_info['distance']:.1f} km")
        st.metric("Total Duration", f"{st.session_state.route_info['duration']:.1f} hours")
        st.metric("Estimated CO₂ Emissions", f"{st.session_state.route_info['emissions']:.2f} kg")
    else:
        st.metric("Total Distance", "0 km")
        st.metric("Total Duration", "0 hours")
        st.metric("Estimated CO₂ Emissions", "0 kg")

    st.markdown("---")
    st.subheader("Vehicle Details")
    st.write(f"Selected Vehicle: {vehicle_type}")
    if st.session_state.route_info['distance'] > 0:
        d = st.session_state.route_info['distance']
        t = st.session_state.route_info['duration']
        if t > 0:
            v_info = {
                "Petrol": {"fuel_type": "Gasoline", "avg": "6-8 L/100km", "co2": "0.192 kg", "range": "400-600 km"},
                "Diesel": {"fuel_type": "Diesel", "avg": "5-7 L/100km", "co2": "0.171 kg", "range": "600-800 km"},
                "Electric": {"fuel_type": "Electricity", "avg": "15-20 kWh/100km", "co2": "0.05 kg", "range": "300-500 km"}
            }
            st.info(f"""
                ### Route Statistics
                - Total Distance: {d:.1f} km
                - Total Duration: {t:.1f} hours
                - Average Speed: {d/t:.1f} km/h
                - CO₂ Emissions: {st.session_state.route_info['emissions']:.2f} kg
                - Fuel Efficiency: {d / st.session_state.route_info['emissions']:.1f} km/kg CO₂

                ### Vehicle Info
                - Fuel Type: {v_info[vehicle_type]['fuel_type']}
                - Avg Consumption: {v_info[vehicle_type]['avg']}
                - CO₂ per km: {v_info[vehicle_type]['co2']}
                - Range: {v_info[vehicle_type]['range']}
            """)
        else:
            st.info("Duration is zero — cannot compute speed/efficiency.")
    else:
        st.info("Select a vehicle and generate route to view stats.")

    st.markdown("---")
    render_quick_actions(pd.DataFrame([
        {"Item": "Laptops", "In Stock": 8, "ETA (hrs)": 3.5},
        {"Item": "Monitors", "In Stock": 2, "ETA (hrs)": 6.0},
        {"Item": "Printers", "In Stock": 1, "ETA (hrs)": 4.0},
        {"Item": "Cables", "In Stock": 25, "ETA (hrs)": 2.0},
    ]))
    st.markdown("---")
    render_route_history()
    render_analytics_summary()

st.markdown("---")
st.markdown("© 2024 PathX - Logistics Optimization Platform")

