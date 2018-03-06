import json
import numpy as np
import argparse
from urllib.parse import unquote
from sumstats.common_constants import *
from flask import url_for
from config import properties
from sumstats.utils.interval import *


def _set_properties():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-config', help='The configuration file to use instead of default')
    args = argparser.parse_args()
    if args.config is not None:
        with open(args.config) as config:
            props = json.load(config)
            properties.output_path = props["output_path"]
            properties.gwas_study_location = props["gwas_study_location"]
            properties.input_path = props["input_path"]
            properties.ols_terms_location = props["ols_terms_location"]


def _create_study_info_for_trait(studies, trait):
    study_list = []
    for study in studies:
        study_info = {'study': study, 'trait': trait,
                      '_links': {'self': _create_href(method_name='get_trait_study_assocs',
                                                      params={'trait': trait, 'study': study}),
                                 'trait': _create_href(method_name='get_trait_assocs', params={'trait': trait})}}

        study_info['_links']['gwas_catalog'] = {'href': str(properties.gwas_study_location + study)}
        study_info['_links']['ols'] = {'href': str(properties.ols_terms_location + trait)}
        study_list.append(study_info)
    return study_list


def _get_array_to_display(datasets, variant=None, chromosome=None):
    if datasets is None: return {}
    if len(datasets[REFERENCE_DSET]) <= 0: return {}

    mantissa_dset = datasets.pop(MANTISSA_DSET)
    exponent_dset = datasets.pop(EXP_DSET)
    datasets[PVAL_DSET] = _reconstruct_pvalue(mantissa_dset=mantissa_dset, exp_dset=exponent_dset)

    data_dict = {}
    length = len(datasets[PVAL_DSET])
    for index in range(length):
        # elements are numpy types, they need to be python types to be json serializable
        element_info = {dset: np.asscalar(np.array(dataset[index])) for dset, dataset in datasets.items()}

        specific_variant = _evaluate_variable(variable=variant, datasets=datasets, dset_name=SNP_DSET, traversal_index=index)
        specific_chromosome = _evaluate_variable(variable=chromosome, datasets=datasets, dset_name=CHR_DSET, traversal_index=index)

        element_info['_links'] = {'self': _create_href(method_name='get_variants',
                                                   params={'variant': specific_variant, 'study_accession': datasets[STUDY_DSET][index],
                                                           'chromosome': specific_chromosome})}
        element_info['_links']['variant'] = _create_href(method_name='get_variants',
                                                         params={'variant': specific_variant, 'chromosome': specific_chromosome})
        element_info['_links']['study'] = _create_href(method_name='get_studies',
                                                       params={'looking_for': datasets[STUDY_DSET][index]})

        data_dict[index] = element_info
    return data_dict


def _reconstruct_pvalue(mantissa_dset, exp_dset):
    pval_array = np.empty(len(mantissa_dset), dtype=vlen_dtype)
    for index, mantissa in enumerate(mantissa_dset):
        pval_array[index] = (str(mantissa) + "e" + str(exp_dset[index]))
    return pval_array.tolist()


def _evaluate_variable(variable, datasets, dset_name, traversal_index):
    if variable is not None:
        return variable
    return datasets[dset_name][traversal_index]


def _create_associations_response(method_name, start, size, index_marker, data_dict, params):
    return {'_embedded': {'associations': data_dict}, '_links': _create_next_links(
        method_name=method_name, start=start, size=size, index_marker=index_marker,
        size_retrieved=len(data_dict),
        params=params
    )}


def _create_next_links(method_name, start, size, index_marker, size_retrieved, params=None):
    params = params or {}
    prev = max(0, start - size)
    start_new = start + index_marker

    response = {'self': _create_href(method_name=method_name, params=params)}
    params['start'] = 0
    params['size'] = size
    response['first'] = _create_href(method_name=method_name, params=params)
    params['start'] = prev
    response['prev'] = _create_href(method_name=method_name, params=params)

    if size_retrieved == size:
        params['start'] = start_new
        response['next'] = _create_href(method_name=method_name, params=params)

    return response


def _create_href(method_name, params=None):
    params = params or {}
    return {'href': unquote(
        url_for(method_name, **params, _external=True)
    )}


def _get_basic_arguments(args):
    start = int(_retrieve_endpoint_arguments(args, "start", 0))
    size = int(_retrieve_endpoint_arguments(args, "size", 20))
    p_lower = _retrieve_endpoint_arguments(args, "p_lower")
    p_upper = _retrieve_endpoint_arguments(args, "p_upper")
    pval_interval = _get_interval(lower=p_lower, upper=p_upper, interval=FloatInterval)
    return start, size, p_lower, p_upper, pval_interval


def _retrieve_endpoint_arguments(args, argument_name, value_if_empty=None):
    try:
        argument = args[argument_name]
    except KeyError:
        argument = value_if_empty
    return argument


def _get_interval(lower, upper, interval):
    if (lower is None) and upper is None:
        return None
    if lower is not None and upper is not None:
        if lower > upper:
            raise ValueError("Lower limit (%s) is bigger than upper limit (%s)." %(lower, upper))
    return interval().set_tuple(lower_limit=lower, upper_limit=upper)