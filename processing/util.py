import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_geojson_grid(upper_right, lower_left, colors, mask_matrix, n=100):
    """Returns a grid of geojson rectangles, and computes the exposure in each section of the grid based on the vessel data.

    Parameters
    ----------
    upper_right: array_like
        The upper right hand corner of "grid of grids".

    lower_left: array_like
        The lower left hand corner of "grid of grids".

    n: integer
        The number of rows/columns in the (n,n) grid.

    Returns
    -------

    list
        List of "geojson style" dictionary objects   
    """

    all_boxes = []

    lat_steps = np.linspace(lower_left[0], upper_right[0], n+1)
    lon_steps = np.linspace(lower_left[1], upper_right[1], n+1)

    cmap = plt.cm.magma
    norm = mpl.colors.Normalize(vmin=0, vmax=1)

    lat_stride = lat_steps[1] - lat_steps[0]
    lon_stride = lon_steps[1] - lon_steps[0]

    for row_idx, lat in enumerate(lat_steps[:-1]):
        for col_idx, lon in enumerate(lon_steps[:-1]):
            # Define dimensions of box in grid
            upper_left = [lon, lat + lat_stride]
            upper_right = [lon + lon_stride, lat + lat_stride]
            lower_right = [lon + lon_stride, lat]
            lower_left = [lon, lat]

            # Define json coordinates for polygon
            coordinates = [
                upper_left,
                upper_right,
                lower_right,
                lower_left,
                upper_left
            ]

            color = cmap(norm(colors[row_idx][col_idx]))
            color = mpl.colors.to_hex(color)

            geo_json = {"type": "FeatureCollection",
                        "properties": {
                            "lower_left": lower_left,
                            "upper_right": upper_right
                        },
                        "features": []}

            grid_feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                },
                "properties": {
                    "show": mask_matrix[row_idx][col_idx],
                    "color": color
                }
            }

            geo_json["features"].append(grid_feature)

            all_boxes.append(geo_json)

    return all_boxes


def addPathLoss(df: pd.DataFrame, gain=0):
    """
    Calculate the path loss in dB.

    Parameters
    ----------
    df : pd.DataFrame containinng the tp and rssi values

    gain: float antenna gain in dB
    Default 0

    """
    df["pl_db"] = df.tp - df.rssi - gain


def addDistanceTo(df: pd.DataFrame, origin):
    lat = origin[0]
    lon = origin[1]

    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : list of float
        [lat, long]
    df : pd.DataFrame
    """

    radius = 6371  # km

    dlat = np.radians(df.lat - lat)
    dlon = np.radians(df.lon - lon)

    a = (np.sin(dlat / 2) * np.sin(dlat / 2) +
         np.cos(np.radians(lat)) * np.cos(np.radians(df.lat)) *
         np.sin(dlon / 2) * np.sin(dlon / 2))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = (radius * c)*1000

    df['distance'] = d
    # TODO add altitude as well ?


def normalize(data, min_val=None, max_val=None, num_bins=None):
    """Return a value between [0,1] scaled with respect to min and max values of the array and made discrete

    Parameters
    ----------

    data: pandas DataFrame or Series 

    min_val: minimum value 
    """

    if not min_val:
        min_val = data.min()
    if not max_val:
        max_val = data.max()

    if num_bins:

        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return (((data-min_val)/abs(max_val-min_val))*(num_bins-1)).astype(int)
        else:
            return ValueError("data needs to be a panda dataframe or series")
    else:
        if isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            return (data-min_val)/abs(max_val-min_val)
        else:
            return ValueError("data needs to be a panda dataframe or series")
