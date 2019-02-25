import pandas as pd

def get_data(hdf, key, fields, condition=None):
    if condition:
        return pd.read_hdf(hdf, key, columns=fields, where=condition, index=False)
    else:
        return pd.read_hdf(hdf, key, columns=fields, index=False)
