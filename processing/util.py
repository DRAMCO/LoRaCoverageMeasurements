"""
    ____  ____      _    __  __  ____ ___
   |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
   | | | | |_) |  / _ \ | |\/| | |  | | | |
   | |_| |  _ <  / ___ \| |  | | |__| |_| |
   |____/|_| \_\/_/   \_\_|  |_|\____\___/
                             research group
                               dramco.be/

    KU Leuven - Technology Campus Gent,
    Gebroeders De Smetstraat 1,
    B-9000 Gent, Belgium

           File: util.py
        Created: 2018-10-26
         Author: Gilles Callebaut
        Version: 1.0
    Description:
"""


import math

import branca.colormap as cm
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_geojson_grid(df, n, plot_snr):
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
    if plot_snr:
        values_to_plot_id = 'snr'
        caption = 'snr'
    else:
        values_to_plot_id = 'rssi'
        caption = 'rss'
    df['lat_discreteat'] = normalize(
        data=df['lat'], num_bins=n)

    df['lon_discrete'] = normalize(
        data=df['lon'], num_bins=n)

    colors = np.zeros((n, n))
    num_values = np.zeros((n, n))
    transparant_matrix = np.zeros((n, n))

    for idx, row in df.iterrows():
        row_idx = int(row['lat_discreteat'])
        col_idx = int(row['lon_discrete'])
        colors[row_idx][col_idx] += row[values_to_plot_id]
        num_values[row_idx][col_idx] += 1
        transparant_matrix[row_idx][col_idx] = 1

    # values == 0 -> = 1 in order to not divide by 
    num_values[num_values < 1 ] = 1
    colors = colors/num_values
    colors = np.nan_to_num(colors)

    max_lat = df['lat'].max()
    max_lon = df['lon'].max()

    min_lat = df['lat'].min()
    min_lon = df['lon'].min()

    upper_right = [max_lat, max_lon]
    lower_left = [min_lat, min_lon]
    center = [lower_left[0]+(upper_right[0]-lower_left[0]) /
              2, lower_left[1]+(upper_right[1]-lower_left[1])/2]

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
                    "show": transparant_matrix[row_idx][col_idx],
                    "color": color,
                    "val": norm(colors[row_idx][col_idx])
                }
            }
            geo_json["features"].append(grid_feature)
            all_boxes.append(geo_json)

    colormap = cm.linear.viridis.scale(
        df[values_to_plot_id].min(), df[values_to_plot_id].max())
    colormap.caption = caption
    return all_boxes, colormap


def addPathLossTo(df: pd.DataFrame, tp=20, gain=0):
    """
    Calculate the path loss in dB.
    Parameters
    ----------
    df : pd.DataFrame containinng the tp and rssi values
    gain: float antenna gain in dB
    Default 0
    """
    df["pl_db"] = tp - df.rssi - gain


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

    radius = 6371*1000  # m

    dlat = np.radians(df.lat - lat)
    dlon = np.radians(df.lon - lon)

    a = (np.sin(dlat / 2) * np.sin(dlat / 2) +
         np.cos(np.radians(lat)) * np.cos(np.radians(df.lat)) *
         np.sin(dlon / 2) * np.sin(dlon / 2))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = (radius * c)

    df['distance'] = d
    # TODO add altitude as well ?


def sort(data):
    data = data[data.sat > 0]
    data = data[data.ageValid > 0]
    data = data[data.hdopVal < 75]
    data = data[data.locValid > 0]
    data = data[data.ageValid > 0]
    data = data[data.rssi < 20]

    return data


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
