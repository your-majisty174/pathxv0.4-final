import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import openrouteservice
import sys
from pathlib import Path

# Add src directory to system path
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from dashboard.inventory import render_inventory_editor

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.api.openrouteservice_client import get_route

# Create mock inventory dataset
inventory_data = pd.DataFrame([
    {"Item": "Laptops", "In Stock": 8, "ETA (hrs)": 3.5},
    {"Item": "Monitors", "In Stock": 2, "ETA (hrs)": 6.0},
    {"Item": "Printers", "In Stock": 1, "ETA (hrs)": 4.0},
    {"Item": "Cables", "In Stock": 25, "ETA (hrs)": 2.0},
])

# Add Status column based on stock levels
inventory_data["Status"] = inventory_data["In Stock"].apply(
    lambda x: "✅ OK" if x >= 5 else "⚠️ Low Stock"
)

def calculate_emissions(distance_km: float, vehicle_type: str) -> float:
    """
    Calculate CO2 emissions based on distance and vehicle type.
    
    Args:
        distance_km: Distance in kilometers
        vehicle_type: Type of vehicle ("Petrol", "Diesel", or "Electric")
        
    Returns:
        Estimated CO2 emissions in kilograms
    """
    # Emission factors in kg CO2 per km
    emission_factors = {
        "Petrol": 0.192,  # kg CO2 per km
        "Diesel": 0.171,  # kg CO2 per km
        "Electric": 0.05   # kg CO2 per km
    }
    
    if vehicle_type not in emission_factors:
        raise ValueError(f"Invalid vehicle type: {vehicle_type}")
        
    return distance_km * emission_factors[vehicle_type]

# Set page config
st.set_page_config(
    page_title="PathX Route Planner",
    page_icon="🗺️",
    layout="wide"
)

# Add custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state for map and route info
if 'map_center' not in st.session_state:
    st.session_state.map_center = [49.41461, 8.681495]  # Default center (Heidelberg)
if 'route_points' not in st.session_state:
    st.session_state.route_points = [
        [49.41461, 8.681495],  # Start point
        [49.420318, 8.687872]  # End point
    ]
if 'route_info' not in st.session_state:
    st.session_state.route_info = {
        'distance': 0,
        'duration': 0,
        'emissions': 0
    }

# Title
st.title("🗺️ PathX Route Planner")

# Sidebar
with st.sidebar:
    st.header("Route Parameters")
    
    # Start and End Coordinates
    st.subheader("Coordinates")
    start_coords = st.text_input("Start (lat, lon)", "49.41461, 8.681495")
    end_coords = st.text_input("End (lat, lon)", "49.420318, 8.687872")
    
    # Vehicle Type Selection
    st.subheader("Vehicle Type")
    vehicle_type = st.selectbox(
        "Select Vehicle Type",
        ["Petrol", "Diesel", "Electric"]
    )
    
    # Get Route Button
    st.markdown("---")
    get_route_btn = st.button("Get Route", type="primary")

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Route Map")
    
    # Always show a map, either with default or updated coordinates
    try:
        # Parse coordinates if button was clicked
        if get_route_btn:
            route_calculated = False
            try:
                start_lat, start_lon = map(float, start_coords.split(','))
                end_lat, end_lon = map(float, end_coords.split(','))
                
                # Validate coordinates
                if not (-90 <= start_lat <= 90 and -180 <= start_lon <= 180):
                    raise ValueError("Invalid start coordinates: must be between -90 to 90 for latitude and -180 to 180 for longitude")
                if not (-90 <= end_lat <= 90 and -180 <= end_lon <= 180):
                    raise ValueError("Invalid end coordinates: must be between -90 to 90 for latitude and -180 to 180 for longitude")
                
                # Round coordinates to 6 decimal places (about 11cm precision)
                start_lat = round(start_lat, 6)
                start_lon = round(start_lon, 6)
                end_lat = round(end_lat, 6)
                end_lon = round(end_lon, 6)
                
                # Prepare coordinates for API call (note: OpenRouteService expects [lon, lat] tuples)
                coords = [(start_lon, start_lat), (end_lon, end_lat)]
                
                # Get route from OpenRouteService
                route_info = get_route(coords)
                
                # The geometry is now a list of coordinates, no need to decode
                route_coords = [(lat, lon) for lon, lat in route_info['geometry']]
                
                # Update session state with new coordinates
                st.session_state.map_center = [(start_lat + end_lat) / 2, (start_lon + end_lon) / 2]
                st.session_state.route_points = route_coords
                
                # Update route info in session state
                st.session_state.route_info = {
                    'distance': route_info['distance'] / 1000,  # Convert to km
                    'duration': route_info['duration'] / 3600,  # Convert to hours
                    'emissions': calculate_emissions(route_info['distance'] / 1000, vehicle_type)
                }
                
                route_calculated = True
                
            except ValueError as e:
                st.error(f"Error parsing coordinates: {str(e)}")
                st.info("Please enter coordinates in the format: 'latitude, longitude'")
            except Exception as e:
                error_msg = str(e)
                if "Could not find routable point" in error_msg:
                    st.error("No route found between the specified coordinates. Please try different locations.")
                    st.info("Make sure the coordinates are near roads or paths that can be routed.")
                else:
                    st.error(f"An error occurred while calculating the route: {error_msg}")
            
            if not route_calculated:
                # If route calculation failed, use default coordinates
                st.session_state.map_center = [49.41461, 8.681495]  # Default center (Heidelberg)
                st.session_state.route_points = [
                    [49.41461, 8.681495],  # Start point
                    [49.420318, 8.687872]  # End point
                ]
        
        # Create map with current center
        m = folium.Map(
            location=st.session_state.map_center,
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Add markers for start and end points
        folium.Marker(
            st.session_state.route_points[0],
            popup='Start',
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        folium.Marker(
            st.session_state.route_points[-1],
            popup='End',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add the route line
        folium.PolyLine(
            locations=st.session_state.route_points,
            color='blue',
            weight=5,
            opacity=1
        ).add_to(m)
        
        # Display the map
        st_folium(m, width=700, height=500)
        
        # Add Inventory Dashboard section
        st.markdown("---")
        st.subheader("📦 Inventory Dashboard")
        render_inventory_editor()

        
        # Display selected coordinates
        st.subheader("Selected Coordinates")
        coords_df = pd.DataFrame({
            "Location": ["Start", "End"],
            "Coordinates": [start_coords, end_coords]
        })
        st.dataframe(coords_df, hide_index=True)

        
    except ValueError as e:
        st.error(f"Error parsing coordinates: {str(e)}")
        st.info("Please enter coordinates in the format: 'latitude, longitude'")
    except Exception as e:
        st.error(f"An error occurred while calculating the route: {str(e)}")

with col2:
    st.subheader("Route Information")
    
    # Show route information if available
    if st.session_state.route_info['distance'] > 0:
        # Show success message
        st.success("Route calculated successfully!")
        
        # Update metrics with values from session state
        st.metric(
            label="Total Distance",
            value=f"{st.session_state.route_info['distance']:.1f} km",
            delta=None
        )
        
        st.metric(
            label="Total Duration",
            value=f"{st.session_state.route_info['duration']:.1f} hours",
            delta=None
        )
        
        # Calculate emissions based on vehicle type
        emissions = st.session_state.route_info['emissions']
        
        st.metric(
            label="Estimated CO₂ Emissions",
            value=f"{emissions:.2f} kg",
            delta=None
        )
    else:
        # Show placeholder metrics if no route calculated
        st.metric(
            label="Total Distance",
            value="0 km",
            delta=None
        )
        
        st.metric(
            label="Total Duration",
            value="0 hours",
            delta=None
        )
        
        st.metric(
            label="Estimated CO₂ Emissions",
            value="0 kg",
            delta=None
        )
    
    # Additional Information
    st.markdown("---")
    st.subheader("Vehicle Details")
    st.write(f"Selected Vehicle: {vehicle_type}")
    
    if st.session_state.route_info['distance'] > 0:
        # Show vehicle-specific information
        duration = st.session_state.route_info['duration']
        if duration > 0:  # Avoid division by zero
            avg_speed = st.session_state.route_info['distance'] / duration
            fuel_efficiency = st.session_state.route_info['distance'] / st.session_state.route_info['emissions']
            
            # Vehicle-specific information
            vehicle_info = {
                "Petrol": {
                    "fuel_type": "Gasoline",
                    "avg_consumption": "6-8 L/100km",
                    "co2_per_km": "0.192 kg",
                    "typical_range": "400-600 km"
                },
                "Diesel": {
                    "fuel_type": "Diesel",
                    "avg_consumption": "5-7 L/100km",
                    "co2_per_km": "0.171 kg",
                    "typical_range": "600-800 km"
                },
                "Electric": {
                    "fuel_type": "Electricity",
                    "avg_consumption": "15-20 kWh/100km",
                    "co2_per_km": "0.05 kg",
                    "typical_range": "300-500 km"
                }
            }
            
            # Route statistics
            st.info(f"""
                ### Route Statistics
                - Total Distance: {st.session_state.route_info['distance']:.1f} km
                - Total Duration: {st.session_state.route_info['duration']:.1f} hours
                - Average Speed: {avg_speed:.1f} km/h
                - Estimated CO₂ Emissions: {st.session_state.route_info['emissions']:.2f} kg
                - Fuel Efficiency: {fuel_efficiency:.1f} km/kg CO₂
                
                ### Vehicle Information
                - Fuel Type: {vehicle_info[vehicle_type]['fuel_type']}
                - Average Consumption: {vehicle_info[vehicle_type]['avg_consumption']}
                - CO₂ Emissions per km: {vehicle_info[vehicle_type]['co2_per_km']}
                - Typical Range: {vehicle_info[vehicle_type]['typical_range']}
            """)
        else:
            st.info("Route duration is zero, cannot calculate speed and efficiency")
    else:
        st.info("""
            ### Vehicle Information
            Select a vehicle type and calculate a route to see detailed information about:
            - Route statistics (distance, duration, speed)
            - Fuel consumption and efficiency
            - Environmental impact
            - Vehicle specifications
        """)

# Footer
st.markdown("---")
st.markdown("© 2024 PathX - Logistics Optimization Platform") 
