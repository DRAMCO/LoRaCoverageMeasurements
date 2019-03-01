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

           File:
        Created: 2018-10-30
         Author: Gilles Callebaut
    Description:
"""

import json
import os

import numpy as np
import pandas as pd
import scipy.io as sio
import util as util
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matlab.engine
from matplotlib.ticker import ScalarFormatter

eng = matlab.engine.start_matlab()

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data_with_censored_data.pkl"

PL_THRESHOLD = 145


# def censorced_ml(x, y, c, t, a_est, s2e):
#
#     x = np.asarray(x)
#     y = np.asarray(y)
#     x0 = [a_est[0], a_est[1], np.log(s2e)]
#     uncensored_mask = np.invert(t)
#     t = np.nonzero(t)[0]
#     uncensored_mask = np.nonzero(uncensored_mask)[0]
#
#     def censoredllh(p):
#         a = np.matrix(p[0:2]).T
#         log_sigma2 = p.item(2)
#
#         xt = np.matrix(x[t, :])
#         yt = np.matrix(y[t]).T
#         xta = xt @ a
#
#         Lt = -0.5 * np.power((yt - xta), 2) / np.exp(log_sigma2) - np.log(np.sqrt(2 * np.pi)) - (log_sigma2 / 2)
#         L_sum = np.sum(Lt)
#         Li = np.log(1 - norm.cdf((c - x[uncensored_mask, :] @ a) / np.exp(log_sigma2 / 2)))
#         return - (L_sum + np.sum(Li))
#
#     pars = optimize.fmin(func=censoredllh, x0=x0, maxfun=20000)
#     return tuple(pars)
#
#
# def censoredvar(x, c, param, param1, param2):
#     pass

with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        LOAD_TEST_DATA = False

        if LOAD_TEST_DATA:
            d = np.linspace(10, 200, num=200)
            d0 = 1
            PLd0 = 20 * np.log10(4 * np.pi * d0 / (3e8 / 5.9e9))  # 47.85881241889156
            n = 2
            sigma = 4
            c = 90
            y = PLd0 + 10 * n * np.log10(d / d0) + sigma * np.random.randn(len(d))
            x = np.column_stack((np.ones((len(y), 1)), 10 * np.log10(d / d0)))

            uncensored_packets_mask = y < c
            censored_packets_mask = np.invert(uncensored_packets_mask)

            yt = y
            yt[censored_packets_mask] = c
            x = np.asmatrix(x)

        else:
            input_file_path = os.path.join(
                input_path, measurement, input_file_name)

            df = pd.read_pickle(input_file_path)
            df = df[df.isPacket > 0]  # censored and uncensored packets
            print(F"Max. Path Loss = {df['pl_db'].max()}")

            censored_packets_mask = np.logical_or(df["isPacket"] == 2, df['pl_db'] > PL_THRESHOLD).values
            print(F" Found {len(censored_packets_mask)} censored packets.")
            uncensored_packets_mask = np.invert(censored_packets_mask)

            df.loc[censored_packets_mask, "isPacket"] = 0
            df.loc[censored_packets_mask, "pl_db"] = PL_THRESHOLD

            num_censored_packets = censored_packets_mask.sum()
            print(F"{num_censored_packets} detected {num_censored_packets * 100 / util.numberOfRows(df):.2f}%")

            df = df[df["distance"] > 1]

            x = np.column_stack((np.ones((util.numberOfRows(df), 1)), 10 * np.log10(df["distance"])))
            x = np.asmatrix(x)
            y = df["pl_db"].values
            c = PL_THRESHOLD

        t = censored_packets_mask
        t_matlab = uncensored_packets_mask * 1

        sio.savemat(F'censored_data_{measurement}.mat', {'y': y, 't': t_matlab, 'c': c, 'x': x})
        (a_est, sigma_est, thetahat, sqrt_Avarhat) = eng.compute_path_loss(F'censored_data_{measurement}.mat', nargout=4)

        PLd0_ols = np.float32(a_est[0])
        n_ols = np.float32(a_est[1])

        PLd0_ml = np.float32(thetahat[0])
        n_ml = np.float32(thetahat[1])
        sigma_ml= np.float32(thetahat[2])


        df_uncensored = df.loc[uncensored_packets_mask]

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)

        plt.xscale('log')
        ax.xaxis.set_major_formatter(ScalarFormatter())
        # ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        ax.scatter(df_uncensored['distance'], df_uncensored['pl_db'],
                   marker='x', label="Measured Path Loss", s=1, c='darkorange')

        d_max = df['distance'].max()
        d = np.arange(2,d_max, dtype=np.float)
        pl_ols = PLd0_ols + 10.0*n_ols*np.log10(d)

        ax.plot(d, pl_ols, ls='-', label="OLS: \mu(d)",
                linewidth=.5, color='k')
        ax.fill_between(d, pl_ols+sigma_est, pl_ols-sigma_est, color='k', alpha=0.2)

        pl_ml = PLd0_ml + 10.0*n_ml*np.log10(d)
        ax.plot(d, pl_ml, ls='-', label="MLS: \mu(d)",
                linewidth=1.5, color='k')
        ax.fill_between(d, pl_ml + sigma_ml, pl_ml - sigma_ml, color='k', alpha=0.2)

        ax.set_xlabel('Log distance (m)')
        ax.set_ylabel('Path Loss (dB)')
        plt.show()

        # OLS with data < threshold

        # a_est = inv(xt.H @ xt) @ xt.H @ np.asmatrix(yt[uncensored_packets_mask]).T
        #
        # sigma2_est = np.var(yt[censored_packets_mask] - xt @ a_est)
        #
        # pl = a_est.item(0)
        # n = a_est.item(1)
        #
        # (pl_ml, n_ml, sigma_ml) = censorced_ml(x, yt, PL_THRESHOLD, t, a_est, sigma2_est)
        #
        # print(F" Estimate   OLS         ML")
        # print(F" PL(d0)     {pl:^10.2f}{pl_ml:^10.2f}")
        # print(F" n          {n:^10.3f}{n_ml:^10.3f}")
        # print(F" sigma      {np.sqrt(sigma2_est):^10.3f}{sigma_ml:^10.3f}")


# def plot_path_loss():
#     x, y = zip(*sorted(zip(df['distance'], df['epl_log'])))
#     ax.plot(x, y, ls='-', label="Expected Path Loss",
#             linewidth=1.5, color='gray')
#     x, y = zip(*sorted(zip(df['distance'], df['epl_free_log'])))
#     ax.plot(x, y, ls='dashed', label="Free Space Path Loss",
#             linewidth=1.5, color='dimgray')
#
#     idx = df['distance'] < 300
#     slope, intercept, r_value, p_value, std_err = stats.linregress(
#         df['distance_log'][idx], df['pl_db'][idx])
#     pl0 = intercept
#     n = slope
#     print(slope, intercept, r_value, p_value, std_err)
#     df['epl_log'] = 10 * n * \
#                     np.log10(df['distance']) + (-10 * n * np.log10(d0) + pl0)
#
#     x, y = zip(*sorted(zip(df['distance'], df['epl_log'])))
#     ax.plot(x, y, ls='-', label="Expected Path Loss (without gray measurements)",
#             linewidth=1.5, color='k')
#
#     plt.legend(framealpha=0.0)


