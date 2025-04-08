# src/dashboard/route_history.py

import streamlit as st

def render_route_history():
    st.subheader("📜 Route History")

    # Simulated route history data
    route_data = [
        {"Route": "Route 1", "From": "49.41, 8.68", "To": "49.42, 8.68", "Distance": "1.2 km", "Duration": "8 mins"},
        {"Route": "Route 2", "From": "49.43, 8.66", "To": "49.44, 8.70", "Distance": "2.5 km", "Duration": "12 mins"},
        {"Route": "Route 3", "From": "49.40, 8.69", "To": "49.41, 8.67", "Distance": "1.8 km", "Duration": "9 mins"},
        {"Route": "Route 4", "From": "49.39, 8.65", "To": "49.40, 8.66", "Distance": "3.0 km", "Duration": "15 mins"},
    ]

    st.table(route_data)

    st.info("This is a simulated view of your recent route history. Future versions will allow filtering, exporting, and analytics over time.")
