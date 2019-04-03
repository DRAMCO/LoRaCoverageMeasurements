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

import matlab.engine
import numpy as np
import pandas as pd
import scipy.io as sio
import scipy.constants

import util as util

eng = matlab.engine.start_matlab()

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data_with_censored_data.pkl"
output_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))

PL_THRESHOLD = 148

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

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = df[df.isPacket > 0]  # censored and uncensored packets
        print(F"Max. Path Loss = {df['pl_db'].max()}")
        print(f"Max. distance {df.loc[df['isPacket'] == 1,['distance']].max()}")


        df = df[df["distance"] > 10]

        censored_packets_mask = np.logical_or(df["isPacket"] == 2, df['pl_db'] > PL_THRESHOLD).values
        print(F" Found {len(censored_packets_mask)} censored packets.")
        uncensored_packets_mask = np.invert(censored_packets_mask)

        df.loc[censored_packets_mask, "isPacket"] = 0
        df.loc[censored_packets_mask, "pl_db"] = PL_THRESHOLD

        num_censored_packets = censored_packets_mask.sum()
        print(F"{num_censored_packets} detected {num_censored_packets * 100 / util.numberOfRows(df):.2f}%")

        x = np.column_stack((np.ones((util.numberOfRows(df), 1)), 10 * np.log10(df["distance"])))
        x = np.asmatrix(x)
        y = df["pl_db"].values
        c = PL_THRESHOLD

        t = censored_packets_mask
        t_matlab = uncensored_packets_mask * 1

        sio.savemat(F'censored_data_{measurement}.mat', {'y': y, 't': t_matlab, 'c': c, 'x': x})
        (a_est, sigma_ols, thetahat, sqrt_Avarhat) = eng.compute_path_loss_with_weights(F'censored_data_{measurement}.mat',
                                                                           nargout=4)
        os.remove(F'censored_data_{measurement}.mat')

        PLd0_ols = np.float32(a_est[0])
        n_ols = np.float32(a_est[1])

        PLd0_ml = np.float32(thetahat[0])
        n_ml = np.float32(thetahat[1])
        sigma_ml = np.float32(thetahat[2])

        output_file = "path_loss_censored_data_with_weights.pkl"
        output_file_path = os.path.join(output_path, measurement, output_file)
        result = {
            "PLd0_ols": PLd0_ols,
            "n_ols": n_ols,
            "sigma_ols": sigma_ols,
            "PLd0_ml": PLd0_ml,
            "n_ml": n_ml,
            "sigma_ml": sigma_ml,
            "df_uncensored": df.loc[uncensored_packets_mask]
        }

        pickle.dump(result, open(output_file_path, "wb"))
