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

import pandas as pd
import util as util
import numpy as np
from numpy.linalg import inv
from scipy import optimize
from scipy.stats import norm

currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data_with_censored_data.pkl"

PL_THRESHOLD = 145


def censorced_ml(x, y, c, t, a_est, s2e):
    # optimset('GradObj','off', 'Largescale','off','MaxFunEvals',20000);
    # pars = fminsearch(@(pars) censoredllh(pars),[a_est;log(s2e)],opts);

    x = np.asarray(x)
    y = np.asarray(y)
    x0 = np.vstack((a_est, np.log(s2e)))

    def censoredllh(p):
        a = p[0:2]
        log_sigma2 = p.item(2)

        L = np.zeros(len(y))
        L[t] = -0.5 * np.power((y[t] - x[t] @ a), 2) / np.exp(log_sigma2) - np.log(np.sqrt(2 * np.pi)) - log_sigma2 / 2
        uncensored_mask = np.invert(t)
        L[uncensored_mask] = np.log(1 - norm.cdf( (c - x[uncensored_mask] @ a) / np.exp(log_sigma2 / 2)))
        return -np.sum(L)

    pars = optimize.fmin(func=censoredllh, x0=x0, maxfun=20000)
    return tuple(pars)


def censoredvar(x, c, param, param1, param2):
    pass


with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print(F"--------------------- PATH LOSS MODEL {measurement} ---------------------")

        LOAD_TEST_DATA = True

        if LOAD_TEST_DATA:
            d = np.array(range(10,200))
            d0 = 1
            PLd0= 20*np.log10(4*np.pi* d0/(3e8/5.9e9))
            n = 2
            sigma = 4
            c = 90
            y = PLd0 + 10 * n * np.log10(d / d0) + sigma * np.random.randn(len(d))
            x = np.column_stack((np.ones((len(y), 1)), 10 * np.log10(d/d0)))

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
            uncensored_packets_mask = np.invert(censored_packets_mask)

            df.loc[censored_packets_mask, "isPacket"] = 0
            df.loc[censored_packets_mask, "pl_db"] = PL_THRESHOLD

            num_censored_packets = censored_packets_mask.sum()
            print(F"{num_censored_packets} detected {num_censored_packets * 100 / util.numberOfRows(df):.2f}%")

            df = df[df["distance"] > 1]

            x = np.column_stack((np.ones((util.numberOfRows(df), 1)), 10 * np.log10(df["distance"])))
            x = np.asmatrix(x)
            yt = df["pl_db"].values

        t = censored_packets_mask
        # OLS with data < threshold
        xt = x[uncensored_packets_mask]
        a_est = inv(xt.H @ xt) @ xt.H @ np.asmatrix(yt[uncensored_packets_mask]).T

        sigma2_est = np.var(yt[censored_packets_mask] - xt @ a_est)

        pl = a_est.item(0)
        n = a_est.item(1)

        (pl_ml, n_ml, sigma_ml) = censorced_ml(x, yt, PL_THRESHOLD, t, a_est, sigma2_est)

        print(' Estimate OLS ML')
        print(F" PL(d0) {pl:.2f} {pl_ml:.2f}")
        print(F" n {n:.3f} {n_ml:.3f}")
        print(F" sigma {np.sqrt(sigma2_est):.3f} {sigma_ml:.3f}")

        # Avarhat = censoredvar(x, c, thetahat(1), thetahat(2), thetahat(3));
