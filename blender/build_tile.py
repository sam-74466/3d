"""Run inside Blender 2.93+: create a lightweight preview from verified GeoJSON."""
import argparse
import json
import sys
from pathlib import Path

import bpy


def material(name, color):
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1.0)
    return result


ROAD = material("asphalt", (0.06, 0.065, 0.07))
BUILDING = material("concrete", (0.45, 0.36, 0.28))


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def cube(name, location, size, style):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(style)
    return obj


def build(features):
    # Preview-only geometry. Source records remain in the GeoJSON and metadata.
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates")
        feature_type = properties.get("highway")
        if geometry.get("type") == "Polygon" and properties.get("building"):
            ring = coordinates[0]
            xs, ys = zip(*ring)
            width, depth = max(xs) - min(xs), max(ys) - min(ys)
            cube("verified_building", ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, 4), (width, depth, 8), BUILDING)
        elif geometry.get("type") == "LineString" and feature_type:
            coords = coordinates
            for start, end in zip(coords, coords[1:]):
                x1, y1 = start; x2, y2 = end
                length = ((x2-x1)**2 + (y2-y1)**2) ** .5
                cube("verified_road_segment", ((x1+x2)/2, (y1+y2)/2, 0), (length, 5, .15), ROAD)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
    clear_scene()
    data = json.loads(Path(arguments.input).read_text(encoding="utf-8"))
    if data.get("crs") != "EPSG:32643":
        raise ValueError("Blender preview requires the metric EPSG:32643 export.")
    build(data["features"])
    bpy.ops.wm.save_as_mainfile(filepath=str(Path(arguments.output).resolve()))


if __name__ == "__main__":
    main()
