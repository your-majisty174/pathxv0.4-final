# %% [markdown]
# # OpenRouteService API Test
# 
# This notebook tests the OpenRouteService API client by:
# 1. Importing the `get_route` function
# 2. Defining sample coordinates
# 3. Getting route information
# 4. Visualizing the route
# 5. Displaying route statistics

# %%
# Import required libraries
import sys
import os
import matplotlib.pyplot as plt

# Add project root to Python path
# Get the current working directory
current_dir = os.getcwd()
# Navigate up to the project root
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# Now import the route function
from src.api.openrouteservice_client import get_route

# %%
# Define sample coordinates (longitude, latitude)
coordinates = [
    (8.681495, 49.41461),   # Heidelberg, Germany
    (8.687872, 49.420318),  # Heidelberg Castle
    (8.6945, 49.4125)       # Heidelberg Old Town
]

# %%
# Get route information
try:
    route_info = get_route(coordinates)
    print(f"Route found successfully!")
except Exception as e:
    print(f"Error: {e}")

# %%
# Print route statistics
if 'route_info' in locals():
    distance_km = route_info['distance'] / 1000  # Convert meters to kilometers
    duration_min = route_info['duration'] / 60   # Convert seconds to minutes
    
    print(f"Total Distance: {distance_km:.2f} km")
    print(f"Total Duration: {duration_min:.2f} minutes")

# %%
# Plot the route
if 'route_info' in locals():
    # Extract coordinates for plotting
    lons = [coord[0] for coord in coordinates]
    lats = [coord[1] for coord in coordinates]
    
    # Create the plot
    plt.figure(figsize=(10, 8))
    
    # Plot the route points
    plt.plot(lons, lats, 'ro-', label='Route Points')
    
    # Add start and end markers
    plt.plot(lons[0], lats[0], 'go', markersize=10, label='Start')
    plt.plot(lons[-1], lats[-1], 'bo', markersize=10, label='End')
    
    # Add labels and title
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Route Visualization')
    plt.legend()
    plt.grid(True)
    
    # Adjust layout and show plot
    plt.tight_layout()
    plt.show() 