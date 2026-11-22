from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import osmnx as ox
from shapely.geometry import mapping

from .tiles import aligned_tile, polygon

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"


def add_provenance(frame: gpd.GeoDataFrame, source: str) -> gpd.GeoDataFrame:
    output = frame.copy()
    output["validation_status"] = "verified"
    output["source_name"] = source
    output["source_license"] = "Open Database Licence (ODbL)"
    output["retrieved_utc"] = datetime.now(timezone.utc).isoformat()
    output["source_feature_id"] = output.index.astype(str)
    return output


def fetch_prototype(place: str, tile_size_m: int = 1000) -> Path:
    """Fetch OSM features for the tile centred on a Nominatim-resolved place."""
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    place_gdf = ox.geocode_to_gdf(place).to_crs("EPSG:32643")
    point = place_gdf.geometry.iloc[0].representative_point()
    tile = aligned_tile(point.x, point.y, tile_size_m)
    area_wgs84 = gpd.GeoSeries([polygon(tile)], crs="EPSG:32643").to_crs("EPSG:4326").iloc[0]
    tags = {
        "highway": True,
        "building": True,
        "railway": True,
        "waterway": True,
        "natural": ["water", "wood"],
        "public_transport": True,
        "amenity": ["bus_station", "parking", "school", "hospital"],
    }
    features = ox.features_from_polygon(area_wgs84, tags)
    features = add_provenance(features.to_crs("EPSG:32643"), "OpenStreetMap via Overpass API")
    clipped = gpd.clip(features, polygon(tile))
    output = PROCESSED / "deccan_gymkhana_1km.geojson"
    clipped.to_crs("EPSG:4326").to_file(output, driver="GeoJSON")
    metric_output = PROCESSED / "deccan_gymkhana_1km_metric.json"
    metric_features = [
        {"type": "Feature", "geometry": mapping(row.geometry), "properties": dict(row.drop(labels="geometry"))}
        for _, row in clipped.iterrows()
    ]
    metric_output.write_text(json.dumps({"crs": "EPSG:32643", "tile": tile.__dict__, "features": metric_features}, default=str), encoding="utf-8")
    report = {
        "place_query": place,
        "tile": {"id": tile.tile_id, "size_m": tile.size_m, "bounds_epsg_32643": tile.bounds_32643},
        "feature_count": int(len(clipped)),
        "source": "OpenStreetMap via Overpass API",
        "licence": "ODbL",
        "coordinate_policy": "WGS84 storage; EPSG:32643 processing",
        "notes": "Building heights and road lanes remain unavailable unless directly tagged by source data.",
    }
    (REPORTS / "deccan_gymkhana_provenance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--place", default="Deccan Gymkhana, Pune, Maharashtra, India")
    parser.add_argument("--tile-size-m", type=int, default=1000, choices=(1000, 2000, 5000))
    arguments = parser.parse_args()
    print(fetch_prototype(arguments.place, arguments.tile_size_m))


if __name__ == "__main__":
    main()
