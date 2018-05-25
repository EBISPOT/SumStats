import time
import pandas as pd
from sumstats.utils import utils
from sumstats.utils.pval import get_mantissa_and_exp_lists


def read_datasets_from_input(tsv, dict_of_data, const):
    if tsv is not None:
        datasets_as_lists = {}
        assert dict_of_data is None, "dict_of_data is ignored"
        print(time.strftime('%a %H:%M:%S'))
        for name in const.TO_LOAD_DSET_HEADERS:
            datasets_as_lists[name] = \
                pd.read_csv(tsv, dtype=const.DSET_TYPES[name], usecols=[name], delimiter="\t").to_dict(orient='list')[name]
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
    utils.assert_datasets_not_empty(datasets_as_lists)

    return utils.create_datasets_from_lists(datasets_as_lists)