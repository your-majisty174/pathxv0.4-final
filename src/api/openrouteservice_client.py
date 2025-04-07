import os
import requests
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
env_path = find_dotenv()
if not env_path:
    raise OpenRouteServiceError("Could not find .env file")
load_dotenv(env_path)

class OpenRouteServiceError(Exception):
    """Custom exception for OpenRouteService API errors"""
    pass

def get_api_key() -> str:
    """
    Get the OpenRouteService API key from environment variables.
    
    Returns:
        str: The API key
        
    Raises:
        OpenRouteServiceError: If API key is not found or invalid
    """
    api_key = os.getenv("ORS_API_KEY")
    if not api_key:
        raise OpenRouteServiceError("ORS_API_KEY environment variable is not set")
    if not api_key.strip():
        raise OpenRouteServiceError("ORS_API_KEY is empty")
    return api_key

def get_route(coordinates: List[Tuple[float, float]], profile: str = "driving-car") -> Dict[str, Any]:
    """
    Get route information from OpenRouteService Directions API.
    
    Args:
        coordinates: List of (longitude, latitude) coordinate pairs
        profile: Transportation mode (default: "driving-car")
    
    Returns:
        Dictionary containing route information (distance, duration, geometry)
    
    Raises:
        OpenRouteServiceError: If API request fails or input is invalid
    """
    # Validate input
    if not coordinates or len(coordinates) < 2:
        raise OpenRouteServiceError("At least two coordinates are required")
    
    for coord in coordinates:
        if not isinstance(coord, tuple) or len(coord) != 2:
            raise OpenRouteServiceError("Coordinates must be (longitude, latitude) tuples")
        if not all(isinstance(x, (int, float)) for x in coord):
            raise OpenRouteServiceError("Coordinates must be numeric values")
    
    # Get API key
    api_key = get_api_key()
    
    # Prepare API request
    url = f"https://api.openrouteservice.org/v2/directions/{profile}/geojson"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    
    # Format coordinates for API (v2 format)
    coordinates_list = [[lon, lat] for lon, lat in coordinates]
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "coordinates": coordinates_list,
                "elevation": False,
                "instructions": False,
                "preference": "fastest",
                "units": "m"
            }
        )
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        if not data.get("features"):
            raise OpenRouteServiceError("No route found")
        
        route = data["features"][0]
        properties = route["properties"]
        geometry = route["geometry"]
        
        # Get summary information from properties
        summary = properties.get("summary", {})
        
        return {
            "distance": summary.get("distance", 0),  # in meters
            "duration": summary.get("duration", 0),  # in seconds
            "geometry": geometry["coordinates"]  # coordinates array
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e.response, 'text'):
            error_msg += f"\nResponse: {e.response.text}"
        raise OpenRouteServiceError(f"API request failed: {error_msg}")
    except (KeyError, IndexError) as e:
        raise OpenRouteServiceError(f"Invalid API response format: {str(e)}")
    except Exception as e:
        raise OpenRouteServiceError(f"Unexpected error: {str(e)}") 