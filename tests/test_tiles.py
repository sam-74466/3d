from pune_twin.tiles import aligned_tile


def test_aligned_tile_contains_input_point():
    tile = aligned_tile(386123.8, 2035123.1, 1000)
    min_x, min_y, max_x, max_y = tile.bounds_32643
    assert min_x <= 386123.8 < max_x
    assert min_y <= 2035123.1 < max_y
    assert tile.size_m == 1000
