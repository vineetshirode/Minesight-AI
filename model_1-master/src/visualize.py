"""
visualize.py — Spatial Layer Diagnostic Map Generation Module
SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel
"""

import os
import matplotlib.pyplot as plt
from src.config import OUTPUTS_DIR

def generate_validation_plots(gdf, df_study):
    print("  Generating diagnostic validation maps...")
    
    # 9-Panel Diagnostic Map
    fig, axes = plt.subplots(3, 3, figsize=(22, 18), dpi=150)
    plt.subplots_adjust(hspace=0.28, wspace=0.22)
    fig.suptitle("MANGANESE INTELLIGENCE — Model 1 Spatial Feature Layer Validation Diagnostics", fontsize=18, fontweight="bold", y=0.98)
    
    # 1. Historical Occurrences & Mines
    ax = axes[0, 0]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Occurrence_Distance_km"], cmap="viridis_r", s=4, alpha=0.6)
    ax.scatter(df_study["Longitude_Decimal"], df_study["Latitude_Decimal"], c="red", marker="^", s=70, edgecolor="black", label="Historical Occurrences (N=18)", zorder=5)
    plt.colorbar(sc, ax=ax, label="Occurrence Distance (km)")
    ax.set_title("1. Occurrence Proximity & Catalog Points", fontweight="bold", fontsize=11)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 2. Elevation Surface (DEM)
    ax = axes[0, 1]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Elevation_m"], cmap="terrain", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="Elevation (m)")
    ax.set_title("2. Topographic Elevation (Copernicus DEM 30m Grid)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 3. Topographic Slope
    ax = axes[0, 2]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Slope_deg"], cmap="magma", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="Slope (degrees)")
    ax.set_title("3. Topographic Slope Angle", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 4. Occurrence Density (KDE)
    ax = axes[1, 0]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Occurrence_Density_Score"], cmap="plasma", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="KDE Density Score (0-100)")
    ax.set_title("4. Mineralization Kernel Density (7.5 km Bandwidth)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 5. Lineament Distance Field
    ax = axes[1, 1]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Lineament_Distance_km"], cmap="inferno_r", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="Lineament Distance (km)")
    ax.set_title("5. Structural Lineament Proximity (Sausar Shear Axis)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 6. Geological Formations
    ax = axes[1, 2]
    uniq_forms = list(gdf["Geological_Formation"].unique())
    form_map = {f: i for i, f in enumerate(uniq_forms)}
    c_vals = [form_map[f] for f in gdf["Geological_Formation"]]
    cmap_cat = plt.colormaps.get_cmap("tab10").resampled(len(uniq_forms))
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=c_vals, cmap=cmap_cat, s=4, alpha=0.8)
    cbar = plt.colorbar(sc, ax=ax, ticks=range(len(uniq_forms)))
    cbar.ax.set_yticklabels([f[:20]+"..." if len(f)>20 else f for f in uniq_forms], fontsize=7)
    ax.set_title("6. Lithostratigraphic Formations (Sausar Group)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 7. Vegetation Index (NDVI)
    ax = axes[2, 0]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["NDVI"], cmap="YlGn", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="NDVI Index")
    ax.set_title("7. MODIS Vegetation Index (NDVI)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 8. Mean Annual Rainfall
    ax = axes[2, 1]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["Rainfall_Annual_mm"], cmap="Blues", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="Rainfall (mm/year)")
    ax.set_title("8. NASA GPM Gridded Precipitation", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    # 9. Land Surface Temperature (LST)
    ax = axes[2, 2]
    sc = ax.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf["LST_Celsius"], cmap="coolwarm", s=4, alpha=0.8)
    plt.colorbar(sc, ax=ax, label="LST (°C)")
    ax.set_title("9. MODIS Land Surface Temperature (LST)", fontweight="bold", fontsize=11)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")

    diag_plot_path = os.path.join(OUTPUTS_DIR, "model1_validation_diagnostics.png")
    plt.savefig(diag_plot_path, bbox_inches="tight", dpi=180)
    plt.close()
    print(f"  [SAVED] 9-panel diagnostics: {diag_plot_path}")

    # Individual Feature Maps
    indiv_maps = [
        ("Elevation_m", "Copernicus DEM Elevation (m)", "terrain", "model1_dem_elevation.png"),
        ("Slope_deg", "Topographic Slope (degrees)", "magma", "model1_slope.png"),
        ("Occurrence_Density_Score", "Manganese Occurrence Kernel Density (0-100)", "plasma", "model1_occurrence_density.png"),
        ("Occurrence_Distance_km", "Distance to Nearest Manganese Occurrence (km)", "viridis_r", "model1_occurrence_proximity.png"),
        ("NDVI", "MODIS NDVI Vegetation Index", "YlGn", "model1_ndvi.png"),
        ("Rainfall_Annual_mm", "NASA GPM Mean Annual Rainfall (mm)", "Blues", "model1_rainfall.png"),
        ("Soil_Moisture_pct", "NASA SMAP Soil Moisture (%)", "PuBuGn", "model1_soil_moisture.png"),
        ("LST_Celsius", "MODIS Land Surface Temperature (°C)", "coolwarm", "model1_lst.png"),
    ]

    for col, title, cmap, filename in indiv_maps:
        plt.figure(figsize=(10, 6.5), dpi=140)
        plt.scatter(gdf["Longitude"], gdf["Latitude"], c=gdf[col], cmap=cmap, s=7, alpha=0.85)
        plt.scatter(df_study["Longitude_Decimal"], df_study["Latitude_Decimal"], c="red", marker="^", s=60, edgecolor="black", label="Historical Occurrences (N=18)", zorder=10)
        plt.colorbar(label=title)
        plt.title(f"Model 1 Spatial Layer — {title}\nSausar Belt Study Region (Balaghat, Bhandara, Nagpur)", fontweight="bold", fontsize=12)
        plt.xlabel("Longitude (°E)")
        plt.ylabel("Latitude (°N)")
        plt.legend(loc="lower right")
        plt.grid(True, linestyle="--", alpha=0.4)
        out_p = os.path.join(OUTPUTS_DIR, filename)
        plt.savefig(out_p, bbox_inches="tight", dpi=140)
        plt.close()
        print(f"  [SAVED] Thematic map: {out_p}")
