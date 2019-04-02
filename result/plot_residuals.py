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
with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        input_file_path = os.path.join(input_path, measurement, input_file)
        print(F"Reading from {input_file_path}")
        result = pickle.load(open(input_file_path, "rb"))

        PLd0_ml = result["PLd0_ml"]
        n_ml = result["n_ml"]
        sigma_ml = result["sigma_ml"]

        df_uncensored = result["df_uncensored"]

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)

        plt.xscale('log')
        ax.xaxis.set_major_formatter(ScalarFormatter())
        # ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        d_mask = df_uncensored['distance'] >= 10

        distances = df_uncensored.loc[d_mask]["distance"]
        path_losses = df_uncensored.loc[d_mask]['pl_db']
        path_losses_model = PLd0_ml + 10.0 * n_ml * np.log10(distances)

        ax.scatter(distances, path_losses - path_losses_model,
                   marker='x', label="Measured Path Loss", s=1, c='0.75')

        ax.set_xlabel(r'Log distance (m)')
        ax.set_ylabel(r'Path Loss residuals(dB)')
        lm.format_axes(ax)
        lm.legend(plt)
        lm.save(plt, F'censored_data_{measurement}_residuals_path_loss.pdf')
