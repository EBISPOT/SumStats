import simplejson
import logging
from flask import request
from collections import OrderedDict
import sumstats.explorer as ex
import sumstats.controller as search
from sumstats.utils.properties_handler import properties
from sumstats.server.error_classes import *
from sumstats.errors.error_classes import *
import sumstats.server.api_utils as apiu


def root():
    response = {
        '_links': OrderedDict([
            ('associations', apiu._create_href(method_name='api.get_assocs')),
            ('molecular_phenotypes', apiu._create_href(method_name='api.get_traits')),
            ('studies', apiu._create_href(method_name='api.get_studies')),
            ('tissues', apiu._create_href(method_name='api.get_tissues')),
            ('genes', apiu._create_href(method_name='api.get_genes')),
            ('chromosomes', apiu._create_href(method_name='api.get_chromosomes'))
        ])
    }
    return simplejson.dumps(response)


def associations():
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/associations. " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    datasets, index_marker = searcher.search_all_assocs(start=start, size=size, pval_interval=pval_interval)

    data_dict = apiu._get_array_to_display(datasets=datasets, reveal=reveal)
    params = dict(p_lower=p_lower, p_upper=p_upper)
    response = apiu._create_response(method_name='api.get_assocs', start=start, size=size, index_marker=index_marker,
                                     data_dict=data_dict, params=params)

    return simplejson.dumps(response, ignore_nan=True)


def traits():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/traits. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    traits = explorer.get_list_of_traits()
    trait_list = apiu._get_trait_list(traits=traits, start=start, size=size)

    response = apiu._create_response(collection_name='trait', method_name='api.get_traits',
                                     start=start, size=size, index_marker=size, data_dict=trait_list)

    return simplejson.dumps(response)


def trait(trait):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.has_trait(trait):
            response = apiu._create_info_for_trait(trait)
            return simplejson.dumps(response, ignore_nan=True)
    except NotFoundError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def trait_associations(trait):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets=datasets, reveal=reveal)
        params = dict(trait=trait, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_response(method_name='api.get_trait_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except NotFoundError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def studies():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    studies = explorer.get_list_of_studies()
    study_list = apiu._get_study_list(studies=studies, start=start, size=size)

    response = apiu._create_response(collection_name='studies', method_name='api.get_studies',
                                     start=start, size=size, index_marker=size, data_dict=study_list)

    return simplejson.dumps(response)


def studies_for_trait(trait):
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/traits/" + trait + "/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        explorer = ex.Explorer(apiu.properties)
        studies = explorer.get_list_of_studies_for_trait(trait)
        study_list = apiu._create_study_info_for_trait(studies, trait)
        end = min(start + size, len(study_list))
        response = apiu._create_response(collection_name='studies', method_name='api.get_studies_for_trait',
                                         start=start, size=size, index_marker=size,
                                         data_dict=study_list[start:end], params=dict(trait=trait))

        return simplejson.dumps(response)
    except NotFoundError as error:
        logging.error("/traits/" + trait + "/studies. " + (str(error)))
        raise RequestedNotFound(str(error))


def trait_study(study, trait=None):
    try:
        # try to find the study's trait by looking for it in the database
        # if it doesn't exist it will raise an error
        trait_found = apiu._find_study_info(study=study)
        # check to see that the trait the study actually belongs to is the same
        # as the trait provided by the user
        if trait_found != trait and trait is not None:
            raise BadUserRequest("Trait-study combination does not exist!")
        response = apiu._create_info_for_study(study=study, trait=trait_found)
        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def trait_study_associations(study, trait=None):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        datasets, index_marker = searcher.search_study(trait=trait, study=study,
                                                       start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets=datasets, reveal=reveal)
        params = dict(trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_response(method_name='api.get_trait_study_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def chromosomes():
    chromosomes_list = []
    for chromosome in range(1, (properties.available_chromosomes + 1)):
        try:
            explorer = ex.Explorer(apiu.properties)
            explorer.has_chromosome(chromosome)
            # adding plus one to include the available_chromosomes number
            chromosome_info = _create_chromosome_info(chromosome)
            chromosomes_list.append(chromosome_info)
        except NotFoundError:
            logging.debug("Chromosome %s does not have data...", str(chromosome))

    response = OrderedDict({'_embedded': {'chromosomes': chromosomes_list}})
    return simplejson.dumps(response)


def chromosome(chromosome):
    try:
        response = _create_chromosome_info(chromosome)
        return simplejson.dumps(response)
    except NotFoundError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def chromosome_associations(chromosome):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
        bp_lower, bp_upper, bp_interval = apiu._get_bp_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, 'study_accession')
    except ValueError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_chromosome(chromosome=chromosome,
                                                            start=start, size=size, study=study,
                                                            pval_interval=pval_interval, bp_interval=bp_interval)
        data_dict = apiu._get_array_to_display(datasets=datasets, chromosome=chromosome, reveal=reveal)

        return _create_chromosome_response(dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                                index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper,
                                                p_lower=p_lower, p_upper=p_upper, study=study))

    except NotFoundError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise RequestedNotFound(str(error))
    except SubgroupError:
        # we have not found bp in chromosome, return empty collection
        data_dict = {}
        index_marker = 0
        return _create_chromosome_response(dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                                index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper,
                                                p_lower=p_lower, p_upper=p_upper, study=study))


def variants(variant, chromosome=None):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
        if study is not None:
            return variant_resource(variant=variant, chromosome=chromosome)
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_snp(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)

        data_dict = apiu._get_array_to_display(datasets=datasets, variant=variant, reveal=reveal)
        params = {'variant_id': variant, 'p_lower': p_lower, 'p_upper': p_upper, 'study_accession': study}
        if chromosome is None:
            method_name = 'api.get_variant'
        else:
            params['chromosome'] = chromosome
            method_name = 'api.get_chromosome_variants'

        response = apiu._create_response(method_name=method_name, start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)
    except (NotFoundError, SubgroupError) as error:
        logging.debug(str(error))
        raise RequestedNotFound(str(error))


def variant_resource(variant, chromosome=None):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, reveal = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_snp(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)
        data_dict = apiu._get_array_to_display(datasets=datasets, variant=variant, reveal=reveal)
        params = {'variant_id': variant, 'study_accession': study}
        if chromosome is not None:
            params['chromosome'] = chromosome
        response = apiu._create_resource_response(data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)
    except (NotFoundError, SubgroupError) as error:
        logging.debug(str(error))
        raise RequestedNotFound(str(error))


def tissues():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    studies = explorer.get_list_of_studies()
    tissues = explorer.get_list_of_tissues()
    study_list = apiu._get_study_list(studies=studies, start=start, size=size)
    tissue_list = apiu._get_tissue_list(tissues=tissues, start=start, size=size)
    response = apiu._create_response(collection_name='tissues', method_name='api.get_tissues',
                                     start=start, size=size, index_marker=size, data_dict=tissue_list)

    return simplejson.dumps(response)


def genes():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/traits. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    traits = explorer.get_list_of_traits()
    trait_list = apiu._get_trait_list(traits=traits, start=start, size=size)

    response = apiu._create_response(collection_name='trait', method_name='api.get_traits',
                                     start=start, size=size, index_marker=size, data_dict=trait_list)

    return simplejson.dumps(response)


def _create_chromosome_info(chromosome):
    explorer = ex.Explorer(apiu.properties)
    if explorer.has_chromosome(chromosome):
        chromosome_info = {'chromosome': chromosome,
                           '_links': {'self': apiu._create_href(method_name='api.get_chromosome',
                                                                params={'chromosome': chromosome}),
                                      'associations': apiu._create_href(method_name='api.get_chromosome_assocs',
                                                                        params={'chromosome': chromosome})}}
        return chromosome_info
    raise NotFoundError("Chromosome " + str(chromosome))


def _create_chromosome_response(search_info):
    params = dict(chromosome=search_info['chromosome'], p_lower=search_info['p_lower'], p_upper=search_info['p_upper'],
                  bp_lower=search_info['bp_lower'], bp_upper=search_info['bp_upper'],
                  study_accession=search_info['study'])
    response = apiu._create_response(method_name='api.get_chromosome_assocs', start=search_info['start'], size=search_info['size'],
                                     index_marker=search_info['index_marker'],
                                     data_dict=search_info['data_dict'], params=params)

    return simplejson.dumps(response, ignore_nan=True)
