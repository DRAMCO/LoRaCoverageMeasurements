r"""
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

           File:
        Created: 2018-10-30
         Author: Gilles Callebaut
    Description:
"""

import json
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
from LatexifyMatplotlib import LatexifyMatplotlib as lm
from matplotlib.ticker import ScalarFormatter

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))

lm.latexify()

input_file = "path_loss_censored_data.pkl"
total_max = -1

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        input_file_path = os.path.join(input_path, measurement, input_file)
        print(F"Reading from {input_file_path}")
        result = pickle.load(open(input_file_path, "rb"))

        df_uncensored = result["df_uncensored"]

        d_max = df_uncensored['distance'].max()
        if d_max > total_max:
            total_max = d_max

fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(1, 1, 1)
plt.xscale('log')
ax.xaxis.set_major_formatter(ScalarFormatter())

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
d = np.arange(10, total_max, dtype=np.float)

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        input_file_path = os.path.join(input_path, measurement, input_file)
        print(F"Reading from {input_file_path}")
        result = pickle.load(open(input_file_path, "rb"))

        PLd0_ols = result["PLd0_ols"]
        n_ols = result["n_ols"]
        sigma_ols = result["sigma_ols"]

        PLd0_ml = result["PLd0_ml"]
        n_ml = result["n_ml"]
        sigma_ml = result["sigma_ml"]

        df_uncensored = result["df_uncensored"]

        pl_ml = PLd0_ml + 10.0 * n_ml * np.log10(d)
        p = ax.plot(d, pl_ml, ls='-', label=F"{measurement}")
        ax.fill_between(x=d, y1= pl_ml - (2 * sigma_ml), y2=pl_ml + (2 * sigma_ml), facecolor=p[0].get_color(), alpha=0.1)

    ax.set_xlabel(r'Log distance (m)')
    ax.set_ylabel(r'Path Loss (dB)')

    lm.format_axes(ax)
    lm.legend(plt)
    lm.save(plt, F'censored_data_all_path_loss.pdf')
