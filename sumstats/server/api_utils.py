import numpy as np
import ast
from urllib.parse import unquote
from sumstats.common_constants import *
from flask import url_for
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler as set_p
from sumstats.utils.interval import *
import sumstats.explorer as ex
from collections import OrderedDict
import logging
from sumstats.utils import register_logger
from sumstats.errors.error_classes import *

logger = logging.getLogger(__name__)
register_logger.register(__name__)


def set_properties():
    set_p.set_properties()


def _get_study_list(studies, start, size):
    study_list = []
    end = min(start + size, len(studies))
    for study in studies[start:end]:
        #trait = _find_study_info(study)
        #study_list.append(_create_study_info_for_trait([study], trait))
        study_list.append(_create_study_info_for_trait([study]))
    return study_list

def _get_study_list_no_info(studies, start, size):
    study_list = []
    end = min(start + size, len(studies))
    for study in studies[start:end]:
        study_list.append([{'study_accession': study}])
    return study_list


def _get_tissue_list(tissues, start, size):
    tissue_list = []
    end = min(start + size, len(tissues))
    for tissue in tissues[start:end]:
        tissue_list.append(_create_info_for_tissue(tissue))
    return tissue_list


def _create_study_info_for_trait(studies, trait=None):
    study_list = []
    for study in studies:
        study_info = _create_info_for_study(study=study, trait=trait)
        study_list.append(study_info)
    return study_list


def _create_info_for_tissue(tissue):
    tissue_info = {'tissue': tissue,
                   '_links': {'self': _create_href(method_name='api.get_tissue', params={'tissue': tissue})}
                   }
    tissue_info['_links']['studies'] = _create_href(method_name='api.get_studies_for_tissue', params={'tissue': tissue})
    tissue_info['_links']['associations'] = _create_href(method_name='api.get_tissue_assocs', params={'tissue': tissue})
    return tissue_info


def _create_info_for_study(study, trait=None):
    if trait:
        study_info = {'study_accession': study,
                      '_links': {'self': _create_href(method_name='api.get_trait_study',
                                                      params={'trait': trait, 'study': study}),
                                 'trait': _create_href(method_name='api.get_traits', params={'study_accession': study})}}

        study_info['_links'] = _add_gwas_catalog_href(info_array=study_info['_links'], study_accession=study)
        study_info['_links']['associations'] = _create_href(method_name='api.get_trait_study_assocs',
                                                            params={'trait': trait, 'study': study})
    else:
        study_info = {'study_accession': study,
                      '_links': {'self': _create_href(method_name='api.get_trait_study',
                                                      params={'study': study}),
                                 'trait': _create_href(method_name='api.get_traits', params={'study_accession': study})}}

        study_info['_links'] = _add_gwas_catalog_href(info_array=study_info['_links'], study_accession=study)
        study_info['_links']['associations'] = _create_href(method_name='api.get_trait_study_assocs',
                                                            params={'study': study})
    return study_info


def _get_metadata_for_study():
    pass



def _get_trait_list(traits, start, size):
    trait_list = []
    end = min(start + size, len(traits))
    for trait in traits[start:end]:
        trait_info = _create_info_for_trait(trait)
        trait_list.append(trait_info)
    return trait_list


def _create_info_for_trait(trait):
    trait_info = {'trait': trait,
                  '_links': {'self': _create_href(method_name='api.get_trait', params={'trait': trait})}}
    trait_info['_links']['studies'] = _create_href(method_name='api.get_studies_for_trait', params={'trait': trait})
    trait_info['_links']['associations'] = _create_href(method_name='api.get_trait_assocs', params={'trait': trait})
    return trait_info


def _add_ontology_href(info_array, trait):
    info_array['ols'] = {'href': str(properties.ols_terms_location + trait)}
    return info_array


def _add_gwas_catalog_href(info_array, study_accession):
    if study_accession.startswith(GWAS_CATALOG_STUDY_PREFIX):
        info_array['gwas_catalog'] = {'href': str(properties.gwas_study_location + study_accession)}
    return info_array


def _get_array_to_display(datasets, variant=None, chromosome=None, reveal=False):
    if datasets is None: return {}
    if len(datasets[REFERENCE_DSET]) <= 0: return {}

    #mantissa_dset = datasets.pop(MANTISSA_DSET)
    #exponent_dset = datasets.pop(EXP_DSET)
    #datasets[PVAL_DSET] = _reconstruct_pvalue(mantissa_dset=mantissa_dset, exp_dset=exponent_dset)

    trait_to_study_cache = {}
    data_dict = {}
    length = len(datasets[PVAL_DSET])

    for index in range(length):
        # elements are numpy types, they need to be python types to be json serializable
        element_info = OrderedDict()
        for dset, dataset in datasets.items():
            element_info = _add_element_depending_on_view(info_array=element_info, dset_name=dset, dataset=dataset, index=index, reveal=reveal)

        # when we are constructing each element's _links we need variant and/or chromosome information for them. If they
        # where not provided in the query, we can find out what they are for each element (index) here.


        specific_variant = _evaluate_variable(variable=variant, datasets=datasets, dset_name=SNP_DSET, traversal_index=index)
        specific_chromosome = _evaluate_variable(variable=chromosome, datasets=datasets, dset_name=CHR_DSET, traversal_index=index)

        element_info = _add_missing_variables(variable=variant, datasets=datasets, dset_name=SNP_DSET, element_info=element_info)
        element_info = _add_missing_variables(variable=chromosome, datasets=datasets, dset_name=CHR_DSET, element_info=element_info)

        study = datasets[STUDY_DSET][index]
        study = _study_acc_from_int(study)
        element_info[STUDY_DSET] = study # update study with prefix
        #trait = datasets[TRAIT_DSET][index]
        #trait = ast.literal_eval(trait)

        #print('get trait')
        trait, trait_to_study_cache = _get_trait_for_study(study, trait_to_study_cache)
        #print('got trait')


        element_info['trait'] = trait

        element_info['_links'] = {'self': _create_href(method_name='api.get_chromosome_variants',
                                                   params={'variant_id': specific_variant, 'study_accession': study,
                                                           'chromosome': specific_chromosome})}
        element_info['_links']['variant'] = _create_href(method_name='api.get_chromosome_variants',
                                                         params={'variant_id': specific_variant, 'chromosome': specific_chromosome})
        element_info['_links']['study'] = _create_href(method_name='api.get_trait_study',
                                                       params={'study': study})
        element_info['_links']['trait'] = [_create_href(method_name='api.get_trait', params={'trait': t}) for t in trait]

        data_dict[index] = element_info
    return data_dict


def _study_acc_from_int(study_int):
    acc_no_len = 6
    return GWAS_CATALOG_STUDY_PREFIX + str(study_int).zfill(acc_no_len)


def _add_element_depending_on_view(info_array, dset_name, dataset, index, reveal=None):
    if reveal == 'raw':
        if dset_name not in TO_DISPLAY_RAW:
            # if reveal is set to 'raw' we don't want to include the harmonised fields, only the raw ones
            return info_array
    elif reveal == 'all':
        # do nothing, display all the information that is returned from the queries
        pass
    else:
        if dset_name not in TO_DISPLAY_DEFAULT:
            # if reveal not set we don't want to include the original fields, only the default ones
            return info_array
        else:
            # if reveal not set we don't want to include the original fields, only the default ones
            # but we still want to remove the 'hm_' prefix from the harmonised fields
            dset_name = dset_name.replace(HARMONISATION_PREFIX, '')

    return _add_dset_index(info_array=info_array, dset_name=dset_name, dataset=dataset, index=index)


def _add_dset_index(info_array, dset_name, dataset, index):
    if index >= len(dataset):
        dataset.append(None)
    if dataset[index] == 'nan':
        # string elements that where empty are saved as the string 'nan'
        # and as such need to be converted and displayed as null like the numbers
        dataset[index] = None
    info_array[dset_name] = np.asscalar(np.array(dataset[index]))
    return info_array


def _get_trait_for_study(study, trait_to_study_cache):
    if study in trait_to_study_cache:
        return trait_to_study_cache[study], trait_to_study_cache
    else:
        trait = _find_study_info(study)
        trait_to_study_cache[study] = trait
    return trait, trait_to_study_cache


def _find_study_info(study, trait=None):
    if trait is None:
        explorer = ex.Explorer(config_properties=properties)
        trait = explorer.get_trait_of_study(study)
    return trait


def _reconstruct_pvalue(mantissa_dset, exp_dset):
    pval_array = np.empty(len(mantissa_dset), dtype=vlen_dtype)
    for index, mantissa in enumerate(mantissa_dset):
        pval_array[index] = (str(mantissa) + "e" + str(exp_dset[index]))
    return pval_array.tolist()


def _evaluate_variable(variable, datasets, dset_name, traversal_index):
    """
    Used to find (in the datasets) the variable that/if it is missing (if it's not passed as None)
    :param variable: None or the value of the variable
    :param datasets: the dictionary of datasets containing the information
    :param dset_name: the name of the dataset that the variable will retrieved from
    :param traversal_index: the index of the datasets that we are currently traversing and want the value to come from
    :return: either what was passed in as the 'variable' value, or what is in the dataset called dset_name, at
    index traversal_index
    """
    if variable is not None:
        return variable
    return datasets[dset_name][traversal_index]


def _add_missing_variables(variable, datasets, dset_name, element_info):
    if variable is not None:
        dset_type = DSET_TYPES[dset_name]
        if DSET_TYPES[dset_name] == object:
            dset_type = str
        element_info.update({dset_name: dset_type(variable)})
    return element_info


def _create_response(method_name, start, size, index_marker, data_dict, params=None, collection_name=None):
    if collection_name is None:
        collection_name = 'associations'
    params = params or {}
    if len(data_dict) > 0:
        return OrderedDict([('_embedded', {collection_name: data_dict}), ('_links', _create_next_links(
            method_name=method_name, start=start, size=size, index_marker=index_marker,
            size_retrieved=len(data_dict),
            params=params
        ))])
    else:
        raise NotFoundError("Request for resource with parameters " + str(params))


def _create_resource_response(data_dict, params):
    if len(data_dict) == 1:
        return data_dict[0]
    elif len(data_dict) == 0:
        raise NotFoundError("Request for resource with parameters " + str(params))


def _create_next_links(method_name, start, size, index_marker, size_retrieved, params=None):
    params = params or {}
    prev = max(0, start - size)
    start_new = index_marker

    response = OrderedDict([('self', _create_href(method_name=method_name, params=params))])
    params['start'] = 0
    params['size'] = size
    response['first'] = _create_href(method_name=method_name, params=params)
    params['start'] = prev
    # response['prev'] = _create_href(method_name=method_name, params=params)

    if size_retrieved == size:
        params['start'] = start_new
        response['next'] = _create_href(method_name=method_name, params=params)

    return response


def _create_href(method_name, params=None):
    params = params or {}
    params['_external'] = True
    return {'href': unquote(
        url_for(method_name, **params)
    )}


def _get_bp_arguments(args):
    bp_lower = _retrieve_endpoint_arguments(args, "bp_lower")
    bp_upper = _retrieve_endpoint_arguments(args, "bp_upper")
    bp_interval = _get_interval(lower=bp_lower, upper=bp_upper, interval=IntInterval)
    return bp_lower, bp_upper, bp_interval


def _get_basic_arguments(args):
    start, size = _get_start_size(args)
    p_lower = _retrieve_endpoint_arguments(args, "p_lower")
    p_upper = _retrieve_endpoint_arguments(args, "p_upper")
    pval_interval = _get_interval(lower=p_lower, upper=p_upper, interval=FloatInterval)
    reveal = _retrieve_endpoint_arguments(args, "reveal", None)
    return start, size, p_lower, p_upper, pval_interval, reveal


def _get_start_size(args):
    start = int(_retrieve_endpoint_arguments(args, "start", 0))
    size = int(_retrieve_endpoint_arguments(args, "size", 20))
    return start, size


def _retrieve_endpoint_arguments(args, argument_name, value_if_empty=None):
    try:
        argument = args[argument_name]
    except KeyError:
        argument = value_if_empty
    return argument


def _get_interval(lower, upper, interval):
    if (lower is None) and upper is None:
        return None
    interval = interval().set_tuple(lower_limit=lower, upper_limit=upper)
    if lower is not None and upper is not None:
        if interval.floor() > interval.ceil():
            raise ValueError("Lower limit (%s) is bigger than upper limit (%s)." %(lower, upper))
    return interval
