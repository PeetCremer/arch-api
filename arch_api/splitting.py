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
    """
    # Transform inputs into GeoDataFrames to enable geometric queries
    # using the coordinate reference system (crs) defined above
    building_limits_df = GeoDataFrame.from_features(building_limits.model_dump(), crs=CRS)
    height_plateaus_df = GeoDataFrame.from_features(height_plateaus.model_dump(), crs=CRS)

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
    features = [feature for feature in split_df.iterfeatures()]
    split = Split(type="FeatureCollection", features=features)

    return split
