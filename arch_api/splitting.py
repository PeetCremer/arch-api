from arch_api.exceptions import SplittingError
from arch_api.models.io import BuildingLimits, HeightPlateaus, Split
from geopandas import GeoDataFrame

# GeoJSON coordinates use 'WGS 84' as coordinate reference system (crs),
# see GeoJSON format specification https://datatracker.ietf.org/doc/html/rfc7946#section-4
# The corresponding authority code is 'EPSG:4326', see https://epsg.io/4326
CRS = "EPSG:4326"

# Tolerance for geometry queries, empirically determined on the
# vaterlandsparken example by checking the height plateau overlap
TOL = 1e-7


def split_building_limits_by_height_plateaus(building_limits: BuildingLimits, height_plateaus: HeightPlateaus) -> Split:
    """
    Split a BuildingLimits by a HeightPlateaus, returning a Split

    Args:
        building_limits (BuildingLimits): The building limits to split
        height_plateaus (HeightPlateaus): The height plateaus to split by

    Returns:
        Split: The split building limits, with elevation information from the height plateaus

    Raises:
        SplittingError: If the height plateaus do not completely cover the building limits
        SplittingError: If the building limits overlap with themselves
        SplittingError: If the height plateaus overlap with themselves
    """
    # Transform inputs into GeoDataFrames to enable geometric queries
    # using the coordinate reference system (crs) defined above
    building_limits_df = GeoDataFrame.from_features(building_limits.model_dump(), crs=CRS)
    height_plateaus_df = GeoDataFrame.from_features(height_plateaus.model_dump(), crs=CRS)

    # Check that the the input geometries do not intersect with themselves
    if check_geometry_overlap(building_limits_df):
        raise SplittingError("The building limits must not overlap with themselves")
    if check_geometry_overlap(height_plateaus_df):
        raise SplittingError("The height plateaus must not overlap with themselves")

    # Check that the height plateaus completely cover the building limits
    #
    # Combine the areas of the polygons
    # see https://shapely.readthedocs.io/en/latest/manual.html#shapely.ops.unary_union
    building_limits_union_df = building_limits_df.unary_union
    height_plateaus_union_df = height_plateaus_df.unary_union
    # Add some tolerance to the points in the height plateaus to account for rounding errors,
    # see https://shapely.readthedocs.io/en/latest/manual.html#object.buffer
    height_plateaus_buffered_union_df = height_plateaus_union_df.buffer(TOL)
    # Check that the combined height plateaus completely cover the building limits
    covers = height_plateaus_buffered_union_df.covers(building_limits_union_df)
    if not covers:
        raise SplittingError("The height plateaus do not completely cover the building limits")

    # The split of the height plateaus by the building limits is their intersection
    # (Since the height plateaus fully cover)
    #
    # keep_geom_type=True because we want no intersections other than polygons (no points or lines)
    split_df = height_plateaus_df.overlay(building_limits_df, keep_geom_type=True, how="intersection")

    # Convert the output back to a FeatureCollection
    features = []
    # Results can be "MultiPolygon". We need to split those up to have a common interface
    for feature in split_df.iterfeatures():
        geometry = feature["geometry"]
        geometry_type = geometry["type"]
        if geometry_type == "MultiPolygon":
            for polygon_coords in geometry["coordinates"]:
                polygon = {**geometry, "coordinates": polygon_coords, "type": "Polygon"}
                features.append({**feature, "geometry": polygon})
        elif geometry_type == "Polygon":
            features.append(feature)
        else:
            raise ValueError(f"Unexpected GeoJson type {geometry_type} in split results")
    split = Split(type="FeatureCollection", features=features)

    return split


def check_geometry_overlap(dataframe: GeoDataFrame) -> bool:
    """
    Checks if the geometries in GeoDataFrame overlap with each other

    Args:
        dataframe (GeoDataFrame): The GeoDataFrame to check. Must only contain Polygon geometries
    Returns:
        bool: True if the geometry overlaps with itself, False otherwise
    """
    # A cheap and robust way to check whether the geometries overlap:
    # They overlap if the sum of the areas of the individual geometries
    # is larger than the area of the union of the geometries
    union_area = dataframe.unary_union.area
    assert isinstance(union_area, float)
    sum_area = dataframe.area.sum()
    assert isinstance(sum_area, float)
    # Allow for some tolerance
    is_overlap = abs(sum_area - union_area) > TOL
    return is_overlap
