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
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/associations. " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    datasets, index_marker = searcher.search(start=start, size=size, pval_interval=pval_interval)

    data_dict = apiu._get_array_to_display(datasets=datasets)
    params = dict(p_lower=p_lower, p_upper=p_upper)
    response = apiu._create_response(method_name='api.get_assocs', start=start, size=size, index_marker=index_marker,
                                     data_dict=data_dict, params=params)

    return simplejson.dumps(response, ignore_nan=True)


def traits():
    args = request.args.to_dict()
    #need to add in study to url if present
    try:
        start, size = apiu._get_start_size(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
    except ValueError as error:
        logging.error("/traits. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    if study:
        traits = explorer.get_trait_of_study(study_to_find=study)
        trait_list = apiu._get_trait_list(traits=traits, start=start, size=size)

        response = apiu._create_response(collection_name='trait', method_name='api.get_traits', params={'study_accession': study},
                                         start=start, size=size, index_marker=size, data_dict=trait_list)
    else:
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
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search(trait=trait, start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets=datasets)
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


def study_list():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/study_list. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    studies = explorer.get_list_of_studies()

    # default size is max unless specified:
    if 'size' not in args:
        size = len(studies)

    study_list = apiu._get_study_list_no_info(studies=studies, start=start, size=size)

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


def studies_for_tissue(tissue):
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/tissues/" + tissue + "/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        explorer = ex.Explorer(apiu.properties)
        studies = explorer.get_studies_of_tissue(tissue)
        study_list = apiu._create_study_info_for_tissue(studies, tissue)
        end = min(start + size, len(study_list))
        response = apiu._create_response(collection_name='studies', method_name='api.get_studies_for_tissue',
                                         start=start, size=size, index_marker=size, data_dict=study_list, params=dict(tissue=tissue))

        return simplejson.dumps(response)
    except NotFoundError as error:
        logging.error("/tissues/" + tissue + "/studies. " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_associations(tissue):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/tissues/" + tissue + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        #trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        datasets, index_marker = searcher.search(tissue=tissue,
                                                       start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets=datasets)
        #params = dict(trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        params = dict(p_lower=p_lower, p_upper=p_upper, tissue=tissue)
        response = apiu._create_response(method_name='api.get_tissue_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_study(study, tissue=None):
    try:

        response = apiu._create_info_for_study(study=study, tissue=tissue)
        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def tissue_study_associations(study, tissue=None):
    args = request.args.to_dict()
    gene = None
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
        gene = apiu._retrieve_endpoint_arguments(args, 'gene')
        trait = apiu._retrieve_endpoint_arguments(args, 'molecular_phenotype')
    except ValueError as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        #trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        #datasets, index_marker = searcher.search_study(trait=trait, study=study,
        #                                               start=start, size=size, pval_interval=pval_interval)
        if tissue:
            datasets, index_marker = searcher.search(tissue=tissue, study=study, trait=trait, gene=gene, 
                                                     start=start, size=size, pval_interval=pval_interval)

            data_dict = apiu._get_array_to_display(datasets=datasets)

            params = dict(tissue=tissue, trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        else:
            datasets, index_marker = searcher.search(study=study, gene=gene,                                                                                                       start=start, size=size, pval_interval=pval_interval)

            data_dict = apiu._get_array_to_display(datasets=datasets)

            params = dict(study=study, p_lower=p_lower, p_upper=p_upper, gene=gene)


        response = apiu._create_response(method_name='api.get_tissue_study_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        logging.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def chromosomes():
    chromosomes = []
    #for chromosome in range(1, (properties.available_chromosomes + 1)):
    try:
        explorer = ex.Explorer(apiu.properties)
        chrom_list = explorer.get_list_of_chroms()
        for chromosome in chrom_list:
            # adding plus one to include the available_chromosomes number
            chromosome_info = _create_chromosome_info(chromosome)
            chromosomes.append(chromosome_info)
    except NotFoundError:
        logging.debug("Chromosome %s does not have data...", str(chromosomes))

    response = OrderedDict({'_embedded': {'chromosomes': chromosomes}})
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
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
        bp_lower, bp_upper, bp_interval = apiu._get_bp_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, 'study_accession')
    except ValueError as error:
        logging.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search(chromosome=chromosome,
                                                            start=start, size=size, study=study,
                                                            pval_interval=pval_interval, bp_interval=bp_interval)
        data_dict = apiu._get_array_to_display(datasets=datasets, chromosome=chromosome)
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
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
        if study is not None:
            return variant_resource(variant=variant, chromosome=chromosome)
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)

        data_dict = apiu._get_array_to_display(datasets=datasets, variant=variant)
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
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
    except ValueError as error:
        logging.debug("/chromosomes/" + chromosome + "/associations/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)
        data_dict = apiu._get_array_to_display(datasets=datasets, variant=variant)
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
        logging.error("/tissues. " + (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    tissues = explorer.get_list_of_tissues()
    tissue_list = apiu._get_tissue_list(tissues=tissues, start=start, size=size)
    response = apiu._create_response(collection_name='tissues', method_name='api.get_tissues',
                                     start=start, size=size, index_marker=size, data_dict=tissue_list)

    return simplejson.dumps(response)


def tissue(tissue):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.get_studies_of_tissue(tissue):
            response = apiu._create_info_for_tissue(tissue)
            return simplejson.dumps(response, ignore_nan=True)
    except NotFoundError as error:
        logging.error("/tissue/" + tissue + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def genes():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        logging.error("/traits. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    genes = explorer.get_list_of_genes()
    gene_list = apiu._get_gene_list(genes=genes, start=start, size=size)

    response = apiu._create_response(collection_name='gene', method_name='api.get_genes',
                                     start=start, size=size, index_marker=size, data_dict=gene_list)
    return simplejson.dumps(response)


def gene(gene):
    try:
        explorer = ex.Explorer(config_properties=properties)
        if explorer.has_gene(gene):
            response = apiu._create_info_for_gene(gene)
            return simplejson.dumps(response, ignore_nan=True)
    except NotFoundError as error:
        logging.error("/genes/" + gene + ". " + (str(error)))
        raise RequestedNotFound(str(error))


def gene_associations(gene):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval, quant_method = apiu._get_basic_arguments(args)
    except ValueError as error:
        logging.error("/traits/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search(gene=gene, start=start, size=size, pval_interval=pval_interval, quant_method=quant_method)

        data_dict = apiu._get_array_to_display(datasets=datasets)
        params = dict(gene=gene, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_response(method_name='api.get_gene_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except NotFoundError as error:
        logging.error("/genes/" + gene + ". " + (str(error)))
        raise RequestedNotFound(str(error))


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
