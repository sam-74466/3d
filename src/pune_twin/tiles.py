from __future__ import annotations

from dataclasses import dataclass
from math import floor

from shapely.geometry import box


@dataclass(frozen=True)
class Tile:
    tile_id: str
    size_m: int
    bounds_32643: tuple[float, float, float, float]


def aligned_tile(x_m: float, y_m: float, size_m: int) -> Tile:
    """Return the EPSG:32643-aligned tile containing a metric coordinate."""
    min_x = floor(x_m / size_m) * size_m
    min_y = floor(y_m / size_m) * size_m
    return Tile(
        tile_id=f"utm43n_{size_m}m_{int(min_x)}_{int(min_y)}",
        size_m=size_m,
        bounds_32643=(min_x, min_y, min_x + size_m, min_y + size_m),
    )


def polygon(tile: Tile):
    return box(*tile.bounds_32643)
