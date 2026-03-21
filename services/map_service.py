"""
Builds interactive Folium maps from itinerary location data.
"""
import folium


# colour coding for different location types
MARKER_COLOURS = {
    "accommodation": "blue",
    "attraction": "red",
    "restaurant": "green",
    "transport": "gray",
    "default": "orange",
}


def create_trip_map(locations: list) -> folium.Map:
    """
    Create a Folium map with markers for each location.

    locations: list of dicts with keys:
        name (str), lat (float), lon (float),
        type (str, optional), notes (str, optional)
    """
    if not locations:
        return folium.Map(location=[20, 0], zoom_start=2)

    # centre map on the average of all coords
    avg_lat = sum(loc["lat"] for loc in locations) / len(locations)
    avg_lon = sum(loc["lon"] for loc in locations) / len(locations)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13, tiles="CartoDB positron")

    for loc in locations:
        colour = MARKER_COLOURS.get(loc.get("type", ""), MARKER_COLOURS["default"])
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=folium.Popup(
                f"<b>{loc['name']}</b><br>{loc.get('notes', '')}",
                max_width=250,
            ),
            tooltip=loc["name"],
            icon=folium.Icon(color=colour, icon="info-sign"),
        ).add_to(m)

    # auto-fit bounds
    bounds = [[loc["lat"], loc["lon"]] for loc in locations]
    m.fit_bounds(bounds, padding=(30, 30))

    return m
