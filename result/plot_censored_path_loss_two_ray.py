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
import scipy


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))


#lm.latexify()


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

        #print(result)

        PLd0_ols = result["PLd0_ols"]
        n_ols = result["n_ols"]
        sigma_ols = result["sigma_ols"]

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


        d_mask = df_uncensored['distance'] >= d_critical
        ax.scatter(df_uncensored.loc[d_mask, ["distance"]], df_uncensored.loc[d_mask, ['pl_db']],
                   marker='x', label="Measured Path Loss", s=1, c='0.75')

        d_max = df_uncensored['distance'].max()
        if d_max > total_max:
            total_max = d_max
        d = np.arange(10, d_max, dtype=np.float)
        pl_ols = PLd0_ols + 10.0 * n_ols * np.log10(d)

        ax.plot(d, pl_ols, ls='-', label=r"OLS: \^\mu(d)",
                linewidth=1, color='0.25')
        ax.plot(d, pl_ols+2*sigma_ols, ls=(0, (5, 10)), linewidth=1, color='0.25')
        ax.plot(d, pl_ols-2*sigma_ols, ls=(0, (5, 10)), linewidth=1, color='0.25')
        #ax.fill_between(d, pl_ols + sigma_est, pl_ols - sigma_est, color='k', alpha=0.2)

        pl_ml = PLd0_ml + 10.0 * n_ml * np.log10(d)
        ax.plot(d, pl_ml, ls='-', label=r"MLS: \^\mu(d)",
                linewidth=1.5, color='k')

        ax.plot(d, pl_ml+2*sigma_ml, ls='--', linewidth=1, color='k')
        ax.plot(d, pl_ml-2*sigma_ml, ls='--', linewidth=1, color='k')

        if measurement == "seaside":
            # Plot Two-ray model
            ht = 1.75  # m
            hr = 1.75
            wavelength = 300/868
            dc = (4*ht*hr)/wavelength


            d = np.arange(10, d_max, dtype=np.float)

            pl_fs = 20*np.log10(d) + 20*np.log10(4 * scipy.constants.pi/wavelength)
            pl_2ray = 40*np.log10(d) - 20*np.log10(ht*hr)

            pl_d0 = pl_ml[0] - pl_fs[0]



            pl_2ray = np.maximum(pl_fs,pl_2ray) + pl_d0

            ax.plot(d, pl_2ray, ls='-', label=r"Two-ray model", linewidth=1, color='b')
           pl_0 = 20*np.log10(d_smaller_dc[0]) - 10*np.log10((ht**2)*(hr**2))
            pl_2ray = pl_0 + 20*np.log10(d_smaller_dc)
            ax.plot(d_smaller_dc, pl_2ray, ls='-', linewidth=1, color='b')

        #ax.fill_between(d, pl_ml + sigma_ml, pl_ml - sigma_ml, color='k', alpha=0.2)
        ax.set_xlabel(r'Log distance (m)')
        ax.set_ylabel(r'Path Loss (dB)')

        lm.format_axes(ax)
        lm.legend(plt)
        plt.show()
        #lm.save(plt, F'censored_data_{measurement}_path_loss.pdf')
