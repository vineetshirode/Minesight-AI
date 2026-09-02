# Model 1 — Exploration Intelligence
**SIH 2026 Problem Statement 26009 — MOIL Ltd. / Ministry of Steel**  
**Platform:** MANGANESE INTELLIGENCE  

---

## 1. Overview
Model 1 (Exploration Intelligence) identifies and prioritizes regional exploration targets across the **Sausar Mobile Belt (SMB)** in Madhya Pradesh and Maharashtra (covering Balaghat, Bhandara, Nagpur, and Chhindwara districts).

It unifies:
- **Historical Occurrences & Producing Mines** (GSI, IBM, MOIL catalogs)
- **Lithostratigraphy & Host Formations** (Mansar Formation host, Lohangi marble, Tirodi Gneiss)
- **Structural Lineament Axis** (Sausar thrust/shear zone)
- **High-Resolution Topography** (Copernicus DEM 30m elevation, slope, terrain roughness)
- **Space Technology Indicators** (MODIS NDVI, NASA GPM Precipitation, NASA SMAP Soil Moisture, MODIS LST)

---

## 2. Directory Structure

```text
model_1/
├── data/
│   ├── raw/
│   │   ├── manganese_occurrences_SIH26009.csv       # National reference occurrences (25 records)
│   │   └── manganese_occurrences_MOIL_study_area.csv# MOIL primary study area occurrences (18 records)
│   └── processed/
│       ├── model1_spatial_features.csv             # 21,067 grid cells x 25 features (7.1 MB)
│       └── model1_spatial_features.geojson         # RFC 7946 GeoJSON vector polygon layer (24.5 MB)
├── src/
│   ├── __init__.py                                 # Package initialisation
│   ├── config.py                                   # Spatial extent, CRS, paths & constants
│   ├── grid_generator.py                           # 1.0 km x 1.0 km UTM 44N grid tessellation
│   ├── feature_engineering.py                      # Multi-source proximity, density & satellite extractors
│   └── visualize.py                                # Visual validation diagnostics generator
├── outputs/                                        # Diagnostic validation plots & thematic maps
│   ├── model1_validation_diagnostics.png          # Consolidated 9-panel diagnostic map
│   ├── model1_dem_elevation.png                   # Topographic elevation map
│   ├── model1_slope.png                           # Slope gradient map
│   ├── model1_occurrence_density.png              # Kernel density estimation map
│   ├── model1_occurrence_proximity.png            # Occurrence proximity map
│   ├── model1_ndvi.png                            # MODIS vegetation index map
│   ├── model1_rainfall.png                        # NASA GPM precipitation map
│   ├── model1_soil_moisture.png                   # NASA SMAP soil moisture map
│   └── model1_lst.png                             # MODIS land surface temperature map
├── MODEL1_DATA_QUALITY_REPORT.md                   # Full spatial lineage, CRS & data quality audit
├── run_pipeline.py                                 # Master pipeline execution script
└── README.md                                       # Architecture & usage documentation
```

---

## 3. Running the Pipeline

To execute the complete Model 1 feature engineering and validation suite:

```bash
cd model_1
python run_pipeline.py
```

---

## 4. Key Spatial Specifications

- **Projected CRS**: `EPSG:32644` (WGS 84 / UTM Zone 44N)
- **Geographic CRS**: `EPSG:4326` (WGS 84 Decimal Degrees)
- **Common Grid Resolution**: $1.0\text{ km} \times 1.0\text{ km}$ ($1000\text{ m}$)
- **Total Valid Study Grid Cells**: **21,067**
- **Null Value Count**: **0 (100% complete)**
