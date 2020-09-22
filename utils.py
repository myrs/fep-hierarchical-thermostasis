import numpy as np


def running_mean(x, window=10, mode='valid', pad=True):
    x = np.pad(x, (window - 1, 0), mode='edge')
    return np.convolve(x, np.ones((window,)) / window, mode='valid')