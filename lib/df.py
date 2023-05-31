import numpy as np
import pandas as pd

def normalize_wvfs(df):
    """Normalize the WVF columns of a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame with WVF columns.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with normalized WVF columns.
    """
    df = df.copy()

    new_wvfs = [df["ADC"][i]/np.max(df["ADC"][i]) for i in range(len(df["ADC"]))]
    df["ADC"] = new_wvfs
    return df