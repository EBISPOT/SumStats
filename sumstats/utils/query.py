import pandas as pd
import numpy as np

def get_data(hdf, key, fields, condition=None):
    if condition:
        return pd.read_hdf(hdf, key, columns=fields, where=condition, index=False)
    else:
        return pd.read_hdf(hdf, key, columns=fields, index=False)

def get_study_metadata(hdf, key):
    return hdf.get_storer(key).attrs.study_metadata

