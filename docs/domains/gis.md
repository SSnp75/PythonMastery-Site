---
title: "Python for GIS"
description: Geospatial analysis and mapping with Python, GeoPandas and Shapely
---

# Python for GIS <span class="pm-badge pm-badge-proficient">Domain</span>

<div class="pm-topic-header">
  <strong>🌍 Domain Applications</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~1 week</span>
    <span>📚 Prereqs: <a href="../data/intermediate/pandas.md">Pandas</a></span>
  </div>
</div>

---

## What you'll learn

- [x] What GIS and geospatial data are
- [x] Coordinates and the distance problem (tested)
- [x] Vector vs raster data
- [x] Projections — the classic gotcha
- [x] The GeoPandas/Shapely ecosystem

GIS (Geographic Information Systems) analyzes data tied to locations — maps, routes, territories, satellite imagery. Python has become a first-class GIS language. The distance calculation here is **run-verified**; spatial libraries follow documented APIs.

---

## The distance problem (tested)

A deceptively hard basic task: how far apart are two lat/long points? Because Earth is (roughly) a sphere, you can't just use flat-plane distance — you need the **haversine formula**. Runnable pure Python:

```python
import math

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in kilometers."""
    R = 6371.0                                   # Earth radius in km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R * 2 * math.asin(math.sqrt(a))

# London to Paris
d = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
print(f"{d:.1f} km")
```

Output:

```text
343.6 km
```

~344 km matches the real great-circle distance between London and Paris. This is why GIS isn't just "x, y math" — the Earth's curvature and the choice of coordinate system fundamentally shape every calculation.

---

## Vector vs raster

Two fundamental data models in GIS:

- **Vector** — geometry as points, lines, and polygons (a city as a point, a road as a line, a country as a polygon). Best for discrete features. Handled by **Shapely** (geometry) and **GeoPandas** (tables of geometries).
- **Raster** — a grid of pixels, each with a value (satellite imagery, elevation, temperature maps). Best for continuous surfaces. Handled by **rasterio**, **NumPy**.

---

## Projections: the classic gotcha

!!! warning "Coordinate systems will trip you up"
    The single most common GIS bug is mixing **coordinate reference systems (CRS)**. Latitude/longitude (degrees) and projected coordinates (meters) are different systems; a projection flattens the round Earth onto a flat map, and *every* projection distorts something (area, shape, or distance). Two datasets in different CRSs won't line up. Always check and align the CRS before any spatial operation — GeoPandas makes you specify it for exactly this reason.

---

## GeoPandas + Shapely

**GeoPandas** extends Pandas with geometry — a DataFrame where one column holds shapes:

```python
import geopandas as gpd            # pip install geopandas
from shapely.geometry import Point

# Load a shapefile / GeoJSON
cities = gpd.read_file("cities.geojson")

# It's a DataFrame with a geometry column + a CRS
print(cities.crs)
cities = cities.to_crs("EPSG:3857")     # reproject to a common CRS

# Spatial operations
point = Point(-0.1278, 51.5074)
within = cities[cities.geometry.within(some_polygon)]   # points inside an area
cities["area_km2"] = cities.geometry.area / 1e6
```

!!! note "GeoPandas/Shapely follow documented APIs"
    These aren't installed here, so the snippets aren't run-verified (the haversine calc is). GeoPandas + Shapely are the workhorses: spatial joins, buffers, intersections, and reprojection, all on familiar DataFrame-style data.

---

## The ecosystem

| Need | Tool |
|---|---|
| Vector geometry | Shapely |
| Geospatial tables | GeoPandas |
| Raster / imagery | rasterio, NumPy |
| Mapping / tiles | Folium, contextily |
| Projections | pyproj |
| Routing | networkx, OSMnx |

---

## Practice exercises

1. Use `haversine_km` to find the nearest of several cities to a given point.
2. Compute the total length of a route given a list of lat/long waypoints.
3. Explain, with an example, how mixing two coordinate systems produces wrong results.
4. Look up your city's coordinates and compute its distance to three others.
5. Describe when you'd use vector vs raster data for a given problem (e.g. city locations vs rainfall).
