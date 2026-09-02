"""
grid_generator.py — Common Spatial Grid Construction Module
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from pyproj import Transformer
from src.config import (
    CRS_WGS84, CRS_UTM44N, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, GRID_RESOLUTION_M
)

def generate_spatial_grid():
    """
    Generates a regular 1.0 km x 1.0 km polygonal mesh over the Sausar Mobile Belt
    study region in UTM Zone 44N (EPSG:32644) and reprojects to WGS 84 (EPSG:4326).
    """
    trans_wgs_to_utm = Transformer.from_crs(CRS_WGS84, CRS_UTM44N, always_xy=True)
    trans_utm_to_wgs = Transformer.from_crs(CRS_UTM44N, CRS_WGS84, always_xy=True)
    
    # Transform bounding corners
    x_min, y_min = trans_wgs_to_utm.transform(LON_MIN, LAT_MIN)
    x_max, y_max = trans_wgs_to_utm.transform(LON_MAX, LAT_MAX)
    
    # Snap to grid resolution
    x_min = np.floor(x_min / GRID_RESOLUTION_M) * GRID_RESOLUTION_M
    y_min = np.floor(y_min / GRID_RESOLUTION_M) * GRID_RESOLUTION_M
    x_max = np.ceil(x_max / GRID_RESOLUTION_M) * GRID_RESOLUTION_M
    y_max = np.ceil(y_max / GRID_RESOLUTION_M) * GRID_RESOLUTION_M
    
    x_coords = np.arange(x_min + GRID_RESOLUTION_M/2, x_max, GRID_RESOLUTION_M)
    y_coords = np.arange(y_min + GRID_RESOLUTION_M/2, y_max, GRID_RESOLUTION_M)
    
    xx, yy = np.meshgrid(x_coords, y_coords)
    easting_flat = xx.flatten()
    northing_flat = yy.flatten()
    
    # Transform centroids back to WGS 84
    lon_flat, lat_flat = trans_utm_to_wgs.transform(easting_flat, northing_flat)
    
    # Filter strictly within geographic bounds
    mask = (lat_flat >= LAT_MIN) & (lat_flat <= LAT_MAX) & (lon_flat >= LON_MIN) & (lon_flat <= LON_MAX)
    
    easting_flat = easting_flat[mask]
    northing_flat = northing_flat[mask]
    lon_flat = lon_flat[mask]
    lat_flat = lat_flat[mask]
    
    n_cells = len(easting_flat)
    grid_ids = [f"GRID_{i+1:05d}" for i in range(n_cells)]
    
    # Create polygonal bounding geometry
    half_w = GRID_RESOLUTION_M / 2.0
    polygons_utm = [
        box(e - half_w, n - half_w, e + half_w, n + half_w)
        for e, n in zip(easting_flat, northing_flat)
    ]
    
    gdf_grid = gpd.GeoDataFrame(
        {
            "Grid_ID": grid_ids,
            "UTM_Easting": easting_flat,
            "UTM_Northing": northing_flat,
            "Latitude": np.round(lat_flat, 6),
            "Longitude": np.round(lon_flat, 6),
        },
        geometry=polygons_utm,
        crs=CRS_UTM44N
    )
    
    # Reproject to WGS 84 for standard GeoJSON and web mapping
    gdf_grid_wgs = gdf_grid.to_crs(CRS_WGS84)
    
    return gdf_grid_wgs, easting_flat, northing_flat, lat_flat, lon_flat
