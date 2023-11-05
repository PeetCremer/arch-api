import argparse
import os
from typing import Any

import fastapi
import geopandas
import matplotlib.pyplot as plt
import requests

# Use the same CRS as in the API
from arch_api.splitting import CRS
from dotenv import load_dotenv

from tests.conftest import load_testcase


class Client:
    def __init__(self, base_url: str, project: str = "test"):
        self.base_url = base_url
        self.project = project

    def create_split(self, testcase_dict: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(f"{self.base_url}/projects/{self.project}/splits", json=testcase_dict)
        assert response.status_code == fastapi.status.HTTP_201_CREATED
        split = response.json()
        assert isinstance(split, dict)
        return split


def visualize_testcase(testcase: str) -> None:
    # Fetch the split result for the testcase from the API
    testcase_dict = load_testcase(testcase)
    client = Client(base_url=os.environ.get("BASE_URL", "http://localhost:8000"))
    testcase_split = client.create_split(testcase_dict)

    # Convert split results into GeoDataFrames
    building_limits = geopandas.GeoDataFrame.from_features(testcase_split["building_limits"], crs=CRS)
    height_plateaus = geopandas.GeoDataFrame.from_features(testcase_split["height_plateaus"], crs=CRS)
    split = geopandas.GeoDataFrame.from_features(testcase_split["split"], crs=CRS)

    # Plot meta configuration
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    fig.suptitle(testcase)
    ax.set_xlabel("Lat")
    ax.set_ylabel("Lon")

    # Plot the GeoDataFrames to ax
    building_limits.plot(ax=ax, edgecolor="black", lw=8, facecolor="none", label="building_limits", zorder=2)
    height_plateaus.plot(ax=ax, edgecolor="blue", lw=3, facecolor="none", label="height_plateaus", zorder=3)
    split.plot(
        ax=ax,
        legend=True,
        column="elevation",
        cmap="spring",
        legend_kwds={"label": "elevation"},
        label="split",
        zorder=1,
    )
    plt.show()


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--testcase", default="vaterlandsparken", help="Name of testcase to visualize")
    parser.add_argument(
        "--base_url", default=os.environ.get("BASE_URL", "http://localhost:8000"), help="Base URL of API"
    )
    args = parser.parse_args()
    visualize_testcase(args.testcase)
