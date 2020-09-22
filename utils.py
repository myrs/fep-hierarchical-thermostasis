import numpy as np


def running_mean(x, window=10, mode='valid', pad=True):
    """ a function allowing to plot smoother graphs by averaging
        values of the several time steps """
    x = np.pad(x, (window - 1, 0), mode='edge')
    return np.convolve(x, np.ones((window,)) / window, mode='valid')