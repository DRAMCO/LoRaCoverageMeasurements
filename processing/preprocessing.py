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

           File: preprocessing.py
        Created: 2018-10-30
         Author: Gilles Callebaut
        Version: 1.0
    Description: Preprocessing raw data coming from Arduino Receiver
                 - concatenates different raw csv files
                 - filters data (e.g., values withouth GPS)
                 - removes unneeded data
                 - sorts by time 
                 - distance to transmitters (CENTER)
                 - PL 
                Stores a pickle file in ../result
"""

import glob
import json
import math
import os

import numpy as np
import pandas as pd

import util as util

HEADER = ["time", "sat", "satValid", "hdopVal", "hdopValid", "vdopVal", "pdopVal", "lat", "lon", "locValid", "age",
          "ageValid", "alt", "altValid", "course", "courseValid", "speed", "speedValid", "rssi", "snr", "freqError",  "sf", "isPacket"]

currentDir = os.path.dirname(os.path.abspath(__file__))
current_path = os.path.abspath(os.path.join(
    currentDir, '..', 'data', 'measurements_2'))
all_files = glob.glob(os.path.join(current_path, "*.csv"))

df_from_each_file = (pd.read_csv(f, sep=',', header=None,
                                 names=HEADER) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)

df = util.filter(df)
df['time'] = pd.to_datetime(
    df['time'], format='%m/%d/%Y %H:%M:%S ', utc=True)


df.sort_values(by='time')

CENTER = [51.0595576, 3.7085241]
util.addDistanceTo(df, CENTER)
util.addPathLossTo(df)

output_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
output_file = "preprocessed_data_{}.pkl".format(
    df['time'].dt.strftime("%Y_%m_%d").iloc[0])
output_file_path = os.path.join(output_path, output_file)
df.to_pickle(output_file_path)
