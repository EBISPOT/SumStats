"""
Used by all the loader scripts in the trait/chr/snp modules to load the
tsv file and make it into a dictionary of Datasets
"""

import sys
import time
import json
import pandas as pd
from sumstats.utils import dataset_utils
from sumstats.utils.pval import get_mantissa_and_exp_lists


def read_datasets_from_input(tsv, dict_of_data, const):
    if tsv is not None:
        datasets_as_lists = {}
        assert dict_of_data is None, "dict_of_data is ignored"
        print(time.strftime('%a %H:%M:%S'))
        for name in const.TO_LOAD_DSET_HEADERS:
            datasets_as_lists[name] = \
                pd.read_csv(tsv, dtype=const.DSET_TYPES[name],
                converters={const.R2_DSET: coerce_zero_and_inf_floats_within_limits,
                            const.MEAN_EXPR_DSET: coerce_zero_and_inf_floats_within_limits#,
                            #const.AC_DSET: reform_int_representation,
                            #const.AN_DSET: reform_int_representation
                            },
                #converters={const.RANGE_U_DSET: coerce_zero_and_inf_floats_within_limits,
                #            const.RANGE_L_DSET: coerce_zero_and_inf_floats_within_limits,
                #            const.HM_RANGE_U_DSET: coerce_zero_and_inf_floats_within_limits,
                #            const.HM_RANGE_L_DSET: coerce_zero_and_inf_floats_within_limits
                #            },
                usecols=[name],
                delimiter="\t").to_dict(orient='list')[name]
        print("Loaded tsv file: ", tsv)
        print(time.strftime('%a %H:%M:%S'))
    else:
        datasets_as_lists = dict_of_data

    return datasets_as_lists


def format_datasets(datasets_as_lists, study, const):
    pval_list = datasets_as_lists[const.PVAL_DSET]

    mantissa_dset, exp_dset = get_mantissa_and_exp_lists(pval_list)
    del datasets_as_lists[const.PVAL_DSET]

    datasets_as_lists[const.MANTISSA_DSET] = mantissa_dset
    datasets_as_lists[const.EXP_DSET] = exp_dset

    datasets_as_lists[const.STUDY_DSET] = [study for _ in range(len(datasets_as_lists[const.MANTISSA_DSET]))]
    dataset_utils.assert_datasets_not_empty(datasets_as_lists)

    return dataset_utils.create_datasets_from_lists(datasets_as_lists)


def coerce_zero_and_inf_floats_within_limits(value):
    if value == 'NA':
        value = 'NaN'
    value = float(value)
    if value == 0.0:
        value = sys.float_info.min
    if value == float('inf'):
        value = sys.float_info.max
    return value

def reform_int_representation(value):
    if value == 'NA' or value is None:
        value = 'NaN'
    return int(value)


def format_metadata(metadata):
    with open(metadata) as f:
        """(1) What if the file doesn't exist!?
           (2) Validate the metadata - json schema?    
        """

        return json.loads(f.read())