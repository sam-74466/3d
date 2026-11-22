# Pune District Digital Twin

This repository builds a geographically accurate, tiled Pune district environment. It does **not** place invented roads or building footprints. Every exported feature is tagged `verified`, `inferred`, or `unavailable`, with source metadata retained beside the data.

## First milestone

`Deccan Gymkhana, Pune` is downloaded from OpenStreetMap, projected from WGS84 to EPSG:32643, clipped to a 1 km × 1 km tile, validated, and converted to a lightweight Blender preview.

## Setup (Windows)

1. Install Python 3.11 (64-bit). The installed Python 3.14 is intentionally not used because GDAL/GeoPandas wheels are not reliably available for it.
2. In PowerShell, from this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the prototype

```powershell
python -m pune_twin.prototype --place "Deccan Gymkhana, Pune, Maharashtra, India"
blender --background --python blender\build_tile.py -- --input data\processed\deccan_gymkhana_1km_metric.json --output outputs\deccan_gymkhana_preview.blend
```

The download step requires Internet access to OpenStreetMap/Nominatim. Review the generated provenance report before using data in a game.

## Scale-up

Use `pune_twin.tiles` to generate 1 km, 2 km, or 5 km aligned tiles. Run one tile per Blender process and keep only the selected LOD loaded.
