import numpy as np
from scipy.signal import savgol_filter

def convert_sampling_rate(wvf, sampling_rate, new_sampling_rate, debug=False):
    time = np.arange(0, len(wvf), 1) / sampling_rate
    new_time = np.arange(0, int(len(wvf)*new_sampling_rate/sampling_rate), 1) / new_sampling_rate
    new_wvf = np.interp(new_time, time, wvf)
    return new_wvf

def apply_smoothing(wvf, smoothing, debug=False):
    return savgol_filter(wvf, smoothing, 3)