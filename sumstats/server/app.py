import simplejson
from flask import Flask, request, make_response
from collections import OrderedDict
from sumstats.utils.interval import *
import sumstats.explorer as ex
import sumstats.controller as search
from sumstats.server.error_classes import *
from sumstats.errors.error_classes import *
import sumstats.server.api_utils as apiu
from cherrypy import log as cherrylog
import logging

logger = logging.getLogger()

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.errorhandler(APIException)
def handle_custom_api_exception(error):
    response = simplejson.dumps(error.to_dict())
    return make_response(response, error.status_code)


@app.errorhandler(404)
def not_found(error):
    return make_response(simplejson.dumps({'message': 'Page Not Found.'}), 404)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(simplejson.dumps({'message': 'Internal Server Error.'}), 500)


@app.route('/')
def root():
    response = {
        '_links': OrderedDict([
            ('associations', apiu._create_href(method_name='get_assocs')),
            ('traits', apiu._create_href(method_name='get_traits')),
            ('studies', apiu._create_href(method_name='get_studies')),
            ('chromosomes', apiu._create_href(method_name='get_chromosomes')),
            ('variant', apiu._create_href(method_name='get_variants',
                                          params={'variant': '{variant_id}', 'chromosome': '{chromosome}'}))
        ])
    }
    return simplejson.dumps(response)


@app.route('/associations')
def get_assocs():
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        cherrylog.error("/associations. " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    datasets, index_marker = searcher.search_all_assocs(start=start, size=size, pval_interval=pval_interval)

    data_dict = apiu._get_array_to_display(datasets)
    params = dict(p_lower=p_lower, p_upper=p_upper)
    response = apiu._create_response(method_name='get_assocs', start=start, size=size, index_marker=index_marker,
                                     data_dict=data_dict, params=params)

    return simplejson.dumps(response, ignore_nan=True)


@app.route('/traits')
def get_traits():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        cherrylog.error("/traits. " + (str(error)))
        raise BadUserRequest(str(error))
    explorer = ex.Explorer(apiu.properties)
    traits = explorer.get_list_of_traits()
    trait_list = apiu._get_trait_list(traits=traits, start=start, size=size)

    response = apiu._create_response(collection_name='traits', method_name='get_traits',
                                     start=start, size=size, index_marker=(start + size), data_dict=trait_list)

    return simplejson.dumps(response)


@app.route('/traits/<string:trait>')
def get_trait_assocs(trait):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        cherrylog.error("/traits/" + trait + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets)
        params = dict(trait=trait, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_response(method_name='get_trait_assocs', start=start, size=size, index_marker=index_marker,
                                         data_dict=data_dict, params=params)
        response['_links']['studies'] = apiu._create_href(method_name='get_studies_for_trait', params={'trait': trait})
        response['_links']['ols'] = apiu._create_ontology_href(trait)

        return simplejson.dumps(response, ignore_nan=True)

    except NotFoundError as error:
        cherrylog.error("/traits/" + trait + ". " + (str(error)))
        raise RequestedNotFound(str(error))


@app.route('/studies')
def get_studies():
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        cherrylog.error("/studies. ", (str(error)))
        raise BadUserRequest(str(error))

    explorer = ex.Explorer(apiu.properties)
    trait_studies = explorer.get_list_of_studies()
    study_list = apiu._get_study_list(trait_studies=trait_studies, start=start, size=size)

    response = apiu._create_response(collection_name='studies', method_name='get_studies',
                                     start=start, size=size, index_marker=(start + size), data_dict=study_list)

    return simplejson.dumps(response)


@app.route('/traits/<string:trait>/studies')
def get_studies_for_trait(trait):
    args = request.args.to_dict()
    try:
        start, size = apiu._get_start_size(args)
    except ValueError as error:
        cherrylog.error("/traits/" + trait + "/studies. " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        explorer = ex.Explorer(apiu.properties)
        studies = explorer.get_list_of_studies_for_trait(trait)
        study_list = apiu._create_study_info_for_trait(studies, trait)
        end = min(start + size, len(study_list))
        response = apiu._create_response(collection_name='studies', method_name='get_studies_for_trait',
                                         start=start, size=size, index_marker=(start + size),
                                         data_dict=study_list[start:end], params=dict(trait=trait))

        return simplejson.dumps(response)
    except NotFoundError as error:
        cherrylog.error("/traits/" + trait + "/studies. " + (str(error)))
        raise RequestedNotFound(str(error))


@app.route('/studies/<study>')
@app.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_study_assocs(study, trait=None):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        cherrylog.error("/studies/" + study + ". " + (str(error)))
        raise BadUserRequest(str(error))

    try:
        trait = apiu._find_study_info(study=study, trait=trait)
        searcher = search.Search(apiu.properties)

        datasets, index_marker = searcher.search_study(trait=trait, study=study,
                                                       start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets)
        params = dict(trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_response(method_name='get_trait_study_assocs', start=start, size=size,
                                         index_marker=index_marker,
                                         data_dict=data_dict, params=params)
        response['_links']['gwas_catalog'] = apiu._create_gwas_catalog_href(study)
        response['_links']['trait'] = apiu._create_href(method_name='get_trait_assocs', params={'trait': trait})

        return simplejson.dumps(response, ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        cherrylog.error("/studies/" + study + ". " + (str(error)))
        raise RequestedNotFound(str(error))


@app.route('/chromosomes')
def get_chromosomes():
    chromosomes_list = []
    for chromosome in range(1, 24):
        chromosome_info = {'chromosome': chromosome,
                           '_links': {'self': apiu._create_href(method_name='get_chromosome_assocs',
                                                           params={'chromosome': chromosome})}}
        chromosomes_list.append(chromosome_info)

    response = OrderedDict({'_embedded': {'chromosomes': chromosomes_list}})
    return simplejson.dumps(response)


@app.route('/chromosomes/<string:chromosome>')
def get_chromosome_assocs(chromosome):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, 'study_accession')
        bp_lower = apiu._retrieve_endpoint_arguments(args, 'bp_lower')
        bp_upper = apiu._retrieve_endpoint_arguments(args, 'bp_upper')
        bp_interval = apiu._get_interval(lower=bp_lower, upper=bp_upper, interval=IntInterval)
    except ValueError as error:
        cherrylog.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_chromosome(chromosome=chromosome,
                                                            start=start, size=size, study=study,
                                                            pval_interval=pval_interval, bp_interval=bp_interval)
        data_dict = apiu._get_array_to_display(datasets, chromosome=chromosome)

        return _return_chromosome_info(dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                            index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper,
                                            p_lower=p_lower, p_upper=p_upper, study=study))

    except NotFoundError as error:
        cherrylog.error("/chromosomes/" + chromosome + ". " + (str(error)))
        raise RequestedNotFound(str(error))
    except SubgroupError:
        # we have not found bp in chromosome, return empty collection
        data_dict = {}
        index_marker = 0
        return _return_chromosome_info(dict(chromosome=chromosome, data_dict=data_dict, start=start, size=size,
                                            index_marker=index_marker, bp_lower=bp_lower, bp_upper=bp_upper,
                                            p_lower=p_lower, p_upper=p_upper, study=study))


def _return_chromosome_info(search_info):
    params = dict(chromosome=search_info['chromosome'], p_lower=search_info['p_lower'], p_upper=search_info['p_upper'],
                  bp_lower=search_info['bp_lower'], bp_upper=search_info['bp_upper'],
                  study_accession=search_info['study'])
    response = apiu._create_response(method_name='get_chromosome_assocs', start=search_info['start'], size=search_info['size'],
                                     index_marker=search_info['index_marker'],
                                     data_dict=search_info['data_dict'], params=params)

    return simplejson.dumps(response, ignore_nan=True)


@app.route('/chromosomes/<string:chromosome>/variants/<string:variant>')
def get_variants(chromosome, variant):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
    except ValueError as error:
        cherrylog.error("/chromosomes/" + chromosome + "/variants/" + variant + ". " + (str(error)))
        raise BadUserRequest(str(error))

    searcher = search.Search(apiu.properties)

    try:
        datasets, index_marker = searcher.search_snp(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)

        data_dict = apiu._get_array_to_display(datasets, variant=variant)
        params = {'variant': variant, 'chromosome': chromosome, 'p_lower': p_lower, 'p_upper': p_upper, 'study_accession': study}
        response = apiu._create_response(method_name='get_variants', start=start, size=size, index_marker=index_marker,
                                         data_dict=data_dict, params=params)

        return simplejson.dumps(response, ignore_nan=True)

    except NotFoundError as error:
        cherrylog.error("/chromosomes/" + chromosome + "/variants/" + variant + ". " + (str(error)))
        raise RequestedNotFound(str(error))
    except SubgroupError as error:
        cherrylog.error("/chromosomes/" + chromosome + "/variants/" + variant + ". " + (str(error)))
        raise RequestedNotFound("Wrong variant id or chromosome. Chromosome: %s, variant %s" %(chromosome, variant))


if __name__ == '__main__':
    print("NAME", __name__)
    apiu.set_properties()
    app.run()