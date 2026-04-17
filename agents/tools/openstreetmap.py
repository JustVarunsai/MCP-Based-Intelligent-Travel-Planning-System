"""
Free alternative to Google Maps using OpenStreetMap services.
 - Nominatim for geocoding (address → coordinates)
 - OSRM for routing (distance + travel time between coords)
No API key required.
"""
import json
import requests
from agno.tools import Toolkit

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1"
HEADERS = {"User-Agent": "travel-planner-app/1.0"}


class OpenStreetMapTools(Toolkit):
    """Free geocoding + routing via OSM. No API key needed."""

    def __init__(self, **kwargs):
        super().__init__(
            name="openstreetmap_tools",
            tools=[self.geocode, self.route, self.distance_matrix],
            **kwargs,
        )

    def geocode(self, location: str) -> str:
        """
        Look up coordinates, full address, and region for a place.

        Args:
            location: A place name, address, or landmark (e.g. "Eiffel Tower, Paris")

        Returns:
            JSON string with lat, lon, display_name, and type.
        """
        try:
            resp = requests.get(
                NOMINATIM_URL,
                params={"q": location, "format": "json", "limit": 1},
                headers=HEADERS,
                timeout=10,
            )
            data = resp.json()
            if not data:
                return json.dumps({"error": f"No results for '{location}'"})
            r = data[0]
            return json.dumps({
                "query": location,
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "display_name": r.get("display_name", ""),
                "type": r.get("type", ""),
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def route(self, from_location: str, to_location: str, mode: str = "driving") -> str:
        """
        Calculate the route, distance, and travel time between two places.

        Args:
            from_location: Starting place name or address
            to_location: Destination place name or address
            mode: Transport mode. One of 'driving', 'walking', 'cycling'.

        Returns:
            JSON with distance_km, duration_minutes, and coordinates used.
        """
        try:
            start = json.loads(self.geocode(from_location))
            end = json.loads(self.geocode(to_location))

            if "error" in start:
                return json.dumps({"error": f"Could not geocode '{from_location}'"})
            if "error" in end:
                return json.dumps({"error": f"Could not geocode '{to_location}'"})

            mode_map = {"driving": "driving", "walking": "foot", "cycling": "bike"}
            profile = mode_map.get(mode, "driving")

            url = f"{OSRM_URL}/{profile}/{start['lon']},{start['lat']};{end['lon']},{end['lat']}"
            resp = requests.get(url, params={"overview": "false"}, timeout=10)
            data = resp.json()
            if not data.get("routes"):
                return json.dumps({"error": "No route found"})

            r = data["routes"][0]
            return json.dumps({
                "from": from_location,
                "to": to_location,
                "mode": mode,
                "distance_km": round(r["distance"] / 1000, 2),
                "duration_minutes": round(r["duration"] / 60, 1),
                "from_coords": [start["lat"], start["lon"]],
                "to_coords": [end["lat"], end["lon"]],
            })
        except Exception as e:
            return json.dumps({"error": str(e)})

    def distance_matrix(self, locations: list, mode: str = "driving") -> str:
        """
        Calculate pairwise distances between several locations.
        Useful for optimising daily visit orders.

        Args:
            locations: List of place names (e.g. ["Eiffel Tower", "Louvre", "Notre Dame"])
            mode: Transport mode. One of 'driving', 'walking', 'cycling'.

        Returns:
            JSON with a matrix of distances (km) and durations (minutes).
        """
        try:
            geos = [json.loads(self.geocode(loc)) for loc in locations]
            for i, g in enumerate(geos):
                if "error" in g:
                    return json.dumps({"error": f"Could not geocode '{locations[i]}'"})

            mode_map = {"driving": "driving", "walking": "foot", "cycling": "bike"}
            profile = mode_map.get(mode, "driving")
            coords_str = ";".join(f"{g['lon']},{g['lat']}" for g in geos)
            url = f"https://router.project-osrm.org/table/v1/{profile}/{coords_str}"
            resp = requests.get(
                url,
                params={"annotations": "distance,duration"},
                timeout=15,
            )
            data = resp.json()

            n = len(locations)
            distances_km = [[round(data["distances"][i][j] / 1000, 2) for j in range(n)] for i in range(n)]
            durations_min = [[round(data["durations"][i][j] / 60, 1) for j in range(n)] for i in range(n)]

            return json.dumps({
                "locations": locations,
                "distances_km": distances_km,
                "durations_min": durations_min,
                "mode": mode,
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
