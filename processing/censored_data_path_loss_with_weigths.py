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

import matlab.engine
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.io as sio
import util as util
from matplotlib.ticker import ScalarFormatter
from LatexifyMatplotlib import LatexifyMatplotlib as lm

eng = matlab.engine.start_matlab()

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))


input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "processed_data_with_censored_data.pkl"
input_file_path = os.path.join(input_path, input_file_name)


lm.latexify()

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    data = pd.read_pickle(input_file_path)

    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        df = data[measurement]["data"]
        d = df["distance"].values
        censored_packets_mask = data[measurement]["censored_packets_mask"]
        uncensored_packets_mask = np.invert(censored_packets_mask)

        t = censored_packets_mask
        t_matlab = uncensored_packets_mask * 1

        mat_file = F'censored_data_{measurement}_with_weights.mat'
        sio.savemat(mat_file, {'y': y, 't': t_matlab, 'c': c, 'd': d, 'x':x})
        (PLd0_ols, n_ols, sigma_ols, PLd0_ml, n_ml, sigma_ml, PLd0_est, n_est,
         sigma_est) = eng.compute_path_loss_with_weights(mat_file,
                                                         nargout=9)

        df_uncensored = df.loc[uncensored_packets_mask]

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)

        plt.xscale('log')
        ax.xaxis.set_major_formatter(ScalarFormatter())
        # ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        d_mask = df_uncensored['distance'] >= 10
        ax.scatter(df_uncensored.loc[d_mask, ["distance"]], df_uncensored.loc[d_mask, ['pl_db']],
                   marker='x', label="Measured Path Loss", s=1, c='0.75')

        d_max = df['distance'].max()
        d = np.arange(10, d_max, dtype=np.float)
        pl_ols = PLd0_ols + 10.0 * n_ols * np.log10(d)

        ax.plot(d, pl_ols, ls='-', label=r"OLS: \^\mu(d)",
                linewidth=1, color='0.25')
        ax.plot(d, pl_ols + 2 * sigma_ols, ls=(0, (5, 10)), linewidth=1, color='0.25')
        ax.plot(d, pl_ols - 2 * sigma_ols, ls=(0, (5, 10)), linewidth=1, color='0.25')
        # ax.fill_between(d, pl_ols + sigma_est, pl_ols - sigma_est, color='k', alpha=0.2)

        pl_ml = PLd0_ml + 10.0 * n_ml * np.log10(d)
        ax.plot(d, pl_ml, ls='-', label=r"MLS: \^\mu(d)",
                linewidth=1.5, color='k')

        ax.plot(d, pl_ml + 2.0 * sigma_ml, ls='--', linewidth=1, color='k')
        ax.plot(d, pl_ml - 2.0 * sigma_ml, ls='--', linewidth=1, color='k')

        pl_ml = PLd0_est + 10.0 * n_est * np.log10(d)
        ax.plot(d, pl_ml, ls='-', label=r"MLS: \^\mu(d), weighted",
                linewidth=1.5, color='k')

        ax.plot(d, pl_ml + 2.0 * np.float32(sigma_est), ls='--', linewidth=1, color='k')
        ax.plot(d, pl_ml - 2.0 * np.float32(sigma_est), ls='--', linewidth=1, color='k')

        ax.set_xlabel(r'Log distance (m)')
        ax.set_ylabel(r'Path Loss (dB)')

        lm.format_axes(ax)
        lm.legend(plt)
        lm.save(plt, F'censored_data_{measurement}_with_weights_path_loss.pdf')
