import pytest
from arch_api.exceptions import SplittingError
from arch_api.models.io import BuildingLimits, HeightPlateaus
from arch_api.splitting import check_geometry_overlap, split_building_limits_by_height_plateaus
from geopandas import GeoDataFrame

from tests.conftest import Testcase


class TestCheckGeometryOverlap:
    @staticmethod
    def common(testcase: Testcase) -> tuple[GeoDataFrame, GeoDataFrame]:
        height_plateaus = testcase["height_plateaus"]
        building_limits = testcase["building_limits"]
        height_plateaus_df = GeoDataFrame.from_features(height_plateaus["features"])
        building_limits_df = GeoDataFrame.from_features(building_limits["features"])
        return height_plateaus_df, building_limits_df

    def test_overlapping_height_plateaus(self, overlapping_height_plateaus_testcase: Testcase) -> None:
        height_plateaus_df, building_limits_df = TestCheckGeometryOverlap.common(overlapping_height_plateaus_testcase)
        assert check_geometry_overlap(height_plateaus_df)
        assert not check_geometry_overlap(building_limits_df)

    def test_overlapping_building_limits(self, overlapping_building_limits_testcase: Testcase) -> None:
        height_plateaus_df, building_limits_df = TestCheckGeometryOverlap.common(overlapping_building_limits_testcase)
        assert not check_geometry_overlap(height_plateaus_df)
        assert check_geometry_overlap(building_limits_df)

    def test_no_overlap(self, vaterlandsparken_testcase: Testcase) -> None:
        height_plateaus_df, building_limits_df = TestCheckGeometryOverlap.common(vaterlandsparken_testcase)
        assert not check_geometry_overlap(height_plateaus_df)
        assert not check_geometry_overlap(building_limits_df)


class TestSplitBuildingLimitsByHeightPlateaus:
    def test_ok(self, vaterlandsparken_testcase: Testcase) -> None:
        split = split_building_limits_by_height_plateaus(
            BuildingLimits(**vaterlandsparken_testcase["building_limits"]),
            HeightPlateaus(**vaterlandsparken_testcase["height_plateaus"]),
        )
        features = split.features
        assert len(features) == 3
        # elevations should be all different
        assert features[0].properties["elevation"] != features[1].properties["elevation"]
        assert features[0].properties["elevation"] != features[2].properties["elevation"]
        assert features[1].properties["elevation"] != features[2].properties["elevation"]

    @staticmethod
    def common_failure(testcase: Testcase, error_msg: str) -> None:
        with pytest.raises(SplittingError, match=error_msg):
            _split = split_building_limits_by_height_plateaus(
                BuildingLimits(**testcase["building_limits"]), HeightPlateaus(**testcase["height_plateaus"])
            )

    def test_overlapping_height_plateaus(self, overlapping_height_plateaus_testcase: Testcase) -> None:
        TestSplitBuildingLimitsByHeightPlateaus.common_failure(
            overlapping_height_plateaus_testcase, "The height plateaus must not overlap with themselves"
        )

    def test_overlapping_building_limits(self, overlapping_building_limits_testcase: Testcase) -> None:
        TestSplitBuildingLimitsByHeightPlateaus.common_failure(
            overlapping_building_limits_testcase, "The building limits must not overlap with themselves"
        )

    def test_height_plateaus_not_covering(self, height_plateaus_not_covering_testcase: Testcase) -> None:
        TestSplitBuildingLimitsByHeightPlateaus.common_failure(
            height_plateaus_not_covering_testcase, "The height plateaus do not completely cover the building limits"
        )
