
import json
import os
import warnings
from math import sqrt

import matplotlib as mpl
#mpl.use('pgf')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st
import seaborn as sns
import statsmodels as sm
import statsmodels.formula.api as smf
from matplotlib.ticker import FormatStrFormatter, ScalarFormatter
from scipy import stats as st
from scipy.stats import norm, normaltest, rayleigh, rice, shapiro
from statsmodels.sandbox.regression.predstd import wls_prediction_std

import distributions as dist
import util as util

mpl.rcParams['figure.figsize'] = (16.0, 12.0)
mpl.style.use('ggplot')

# Create models from data


def best_fit_distribution(data, bins=200, ax=None):
    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Distributions to check
    DISTRIBUTIONS = [
        st.alpha, st.anglit, st.arcsine, st.beta, st.betaprime, st.bradford, st.burr, st.cauchy, st.chi, st.chi2, st.cosine,
        st.dgamma, st.dweibull, st.erlang, st.expon, st.exponnorm, st.exponweib, st.exponpow, st.f, st.fatiguelife, st.fisk,
        st.foldcauchy, st.foldnorm, st.frechet_r, st.frechet_l, st.genlogistic, st.genpareto, st.gennorm, st.genexpon,
        st.genextreme, st.gausshyper, st.gamma, st.gengamma, st.genhalflogistic, st.gilbrat, st.gompertz, st.gumbel_r,
        st.gumbel_l, st.halfcauchy, st.halflogistic, st.halfnorm, st.halfgennorm, st.hypsecant, st.invgamma, st.invgauss,
        st.invweibull, st.johnsonsb, st.johnsonsu, st.ksone, st.kstwobign, st.laplace, st.levy, st.levy_l, st.levy_stable,
        st.logistic, st.loggamma, st.loglaplace, st.lognorm, st.lomax, st.maxwell, st.mielke, st.nakagami, st.ncx2, st.ncf,
        st.nct, st.norm, st.pareto, st.pearson3, st.powerlaw, st.powerlognorm, st.powernorm, st.rdist, st.reciprocal,
        st.rayleigh, st.rice, st.recipinvgauss, st.semicircular, st.t, st.triang, st.truncexpon, st.truncnorm, st.tukeylambda,
        st.uniform, st.vonmises, st.vonmises_line, st.wald, st.weibull_min, st.weibull_max, st.wrapcauchy
    ]

    # Best holders
    best_distribution = st.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:

        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))

                # if axis pass in add to plot
                try:
                    if ax:
                        pd.Series(pdf, x).plot(ax=ax)
                except Exception:
                    pass

                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse

        except Exception:
            pass

    return (best_distribution.name, best_params)


def make_pdf(dist, params, size=10000):
    """Generate distributions's Probability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc,
                     scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc,
                   scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = pd.Series(y, x)

    return pdf

SPINE_COLOR = 'gray'
FORMAT = "png"
MARKER = "+"
NUM_BINS = 100



currentDir = os.path.dirname(os.path.abspath(__file__))
path_to_measurements = os.path.abspath(os.path.join(
    currentDir, '..', 'data'))
input_path = os.path.abspath(os.path.join(
    currentDir, '..', 'result'))
input_file_name = "preprocessed_data.pkl"



with open(os.path.join(path_to_measurements, "measurements.json")) as f:
    config = json.load(f)
    measurements = config["measurements"]
    for measurement in measurements:
        print("--------------------- RSS MODEL {} ---------------------".format(measurement))
        
        CENTER = config[measurement]["center"]

        input_file_path = os.path.join(
            input_path, measurement, input_file_name)

        df = pd.read_pickle(input_file_path)
        df = util.onlyPackets(df)

        fig = plt.figure(figsize=(4, 3))
        ax = fig.add_subplot(1, 1, 1)

        output_fig_pgf = os.path.join(
            input_path, 'small_scale_fading_{}.{}'.format(measurement, FORMAT))

        df['distance_bins'], bins = pd.cut(
            x=df.distance, bins=NUM_BINS, retbins=True)

        gb = df.groupby('distance_bins')
        #df_per_distance_bin = [gb.get_group(x) for x in gb.groups]

        #for df_dist_bin in df_per_distance_bin:
        for name, group in gb:
            data = group['rss']

            # Plot for comparison
            ax = sns.distplot(data)
            # Save plot limits
            dataYLim = ax.get_ylim()

            # Find best fit distribution
            best_fit_name, best_fit_params = best_fit_distribution(data, 200, ax)
            best_dist = getattr(st, best_fit_name)

            # Update plots
            ax.set_ylim(dataYLim)
            ax.set_title(u'All Fitted Distributions')
            ax.set_xlabel(u'RSS')
            ax.set_ylabel('Frequency')

            # Make PDF with best params
            pdf = make_pdf(best_dist, best_fit_params)

            # Display
            plt.figure(figsize=(12, 8))
            ax = pdf.plot(lw=2, label='PDF', legend=True)
            data.plot(kind='hist', bins=50, normed=True,
                      alpha=0.5, label='Data', legend=True, ax=ax)

            param_names = (best_dist.shapes +
                           ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
            param_str = ', '.join(['{}={:0.2f}'.format(k, v)
                                   for k, v in zip(param_names, best_fit_params)])
            dist_str = '{}({})'.format(best_fit_name, param_str)

            ax.set_title(u'best fit distribution \n' + dist_str)
            ax.set_xlabel(u'RSS')
            ax.set_ylabel('Frequency')
            plt.show()
