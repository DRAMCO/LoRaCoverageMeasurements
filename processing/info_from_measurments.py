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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data_with_censored_data.pkl"
output_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))

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

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)

        data_packets = df.loc[df['isPacket'] == 1, :]
        print(F"Max. Path Loss = {df['pl_db'].max()}")
        print(f"Max. distance {data_packets['distance'].max()}")
        print(f"Number of received packets {len(data_packets)}")
        sns.distplot(data_packets['distance'], bins=100)

        #sns.distplot(data_packets['pl_db'], bins=10)
        plt.show(block=True)
