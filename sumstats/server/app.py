import simplejson
from flask import Flask, request, make_response
from collections import OrderedDict
from sumstats.utils.interval import *
import sumstats.explorer as ex
import sumstats.search as search
from sumstats.server.error_classes import *
from sumstats.errors.error_classes import *
import sumstats.server.api_utils as apiu
from sumstats.server.api_utils import properties

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
def not_found(error):
    return make_response(simplejson.dumps({'message': 'Internal Server Error.'}), 500)


@app.route('/')
def root():
    response = {
        '_links': {
            'associations': apiu._create_href(method_name='get_assocs'),
            'traits': apiu._create_href(method_name='get_traits'),
            'studies': apiu._create_href(method_name='get_studies'),
            'chromosomes': apiu._create_href(method_name='get_chromosomes'),
            'variant': apiu._create_href(method_name='get_variants', params={'variant': '{variant_id}',
                                                                        'chromosome': '{chromosome}'})
        }
    }
    return simplejson.dumps(OrderedDict(response))


@app.route('/associations')
def get_assocs():
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        raise BadUserRequest(str(error))

    searcher = search.Search(properties.output_path)

    datasets, index_marker = searcher.search_all_assocs(start=start, size=size, pval_interval=pval_interval)

    data_dict = apiu._get_array_to_display(datasets)
    params = dict(p_lower=p_lower, p_upper=p_upper)
    response = apiu._create_associations_response(method_name='get_assocs', start=start, size=size, index_marker=index_marker,
                                             data_dict=data_dict, params=params)

    return simplejson.dumps(OrderedDict(response), ignore_nan=True)


@app.route('/traits')
def get_traits():
    explorer = ex.Explorer(properties.output_path)
    trait_list = []
    traits = explorer.get_list_of_traits()
    for trait in traits:
        trait_info = {'trait': trait,
                      '_links': {'self': apiu._create_href(method_name='get_trait_assocs', params={'trait': trait})}}
        trait_info['_links']['studies'] = apiu._create_href(method_name='get_studies_for_trait', params={'trait': trait})
        trait_info['_links']['ols'] = {'href': str(properties.ols_terms_location + trait)}

        trait_list.append(trait_info)

    response = {'_embedded': {'traits': trait_list}}
    return simplejson.dumps(OrderedDict(response))


@app.route('/traits/<string:trait>')
def get_trait_assocs(trait):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        raise BadUserRequest(str(error))

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets)
        params = dict(trait=trait, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_associations_response(method_name='get_trait_assocs', start=start, size=size, index_marker=index_marker,
                                                 data_dict=data_dict, params=params)
        response['_links']['studies'] = apiu._create_href(method_name='get_studies_for_trait', params={'trait': trait})

        return simplejson.dumps(OrderedDict(response), ignore_nan=True)

    except NotFoundError as error:
        raise RequestedNotFound(str(error))


@app.route('/studies')
@app.route('/studies/<looking_for>')
def get_studies(looking_for=None):
    explorer = ex.Explorer(properties.output_path)
    study_list = []
    trait_studies = []
    if looking_for is not None:
        try:
            trait_studies.append(explorer.get_info_on_study(looking_for))
        except NotFoundError as error:
            raise RequestedNotFound(str(error))
    else:
        trait_studies = explorer.get_list_of_studies()
    for trait_study in trait_studies:
        trait = trait_study.split(":")[0]
        study = trait_study.split(":")[1]

        study_list.append(apiu._create_study_info_for_trait([study], trait))

    response = {'_embedded': {'studies': study_list}}
    return simplejson.dumps(OrderedDict(response))


@app.route('/traits/<string:trait>/studies')
def get_studies_for_trait(trait):
    explorer = ex.Explorer(properties.output_path)
    try:
        studies = explorer.get_list_of_studies_for_trait(trait)
        study_list = apiu._create_study_info_for_trait(studies, trait)
        response = {'_embedded': {'studies': study_list}}
        return simplejson.dumps(OrderedDict(response))
    except NotFoundError as error:
        raise RequestedNotFound(str(error))


@app.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_study_assocs(trait, study):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
    except ValueError as error:
        raise BadUserRequest(str(error))

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_study(trait=trait, study=study,
                                                       start=start, size=size, pval_interval=pval_interval)

        data_dict = apiu._get_array_to_display(datasets)
        params = dict(trait=trait, study=study, p_lower=p_lower, p_upper=p_upper)
        response = apiu._create_associations_response(method_name='get_trait_study_assocs', start=start, size=size, index_marker=index_marker,
                                                 data_dict=data_dict, params=params)

        return simplejson.dumps(OrderedDict(response), ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        raise RequestedNotFound(str(error))


@app.route('/chromosomes')
def get_chromosomes():
    chromosomes_list = []
    for chromosome in range(1, 24):
        chromosome_info = {'chromosome': chromosome,
                           '_links': {'self': apiu._create_href(method_name='get_chromosome_assocs',
                                                           params={'chromosome': chromosome})}}
        chromosomes_list.append(chromosome_info)

    response = {'_embedded': {'chromosomes': chromosomes_list}}
    return simplejson.dumps(OrderedDict(response))


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
        raise BadUserRequest(str(error))

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_chromosome(chromosome=chromosome,
                                                            start=start, size=size, study=study,
                                                            pval_interval=pval_interval, bp_interval=bp_interval)
        data_dict = apiu._get_array_to_display(datasets, chromosome=chromosome)
        _check_bp_group_empty(data_dict=data_dict, chromosome=chromosome, bp_lower=bp_lower, bp_upper=bp_upper)

        params = dict(chromosome=chromosome, p_lower=p_lower, p_upper=p_upper, bp_lower=bp_lower, bp_upper=bp_upper,
                      study_accession=study)
        response = apiu._create_associations_response(method_name='get_chromosome_assocs', start=start, size=size, index_marker=index_marker,
                                                 data_dict=data_dict, params=params)

        return simplejson.dumps(OrderedDict(response), ignore_nan=True)

    except (NotFoundError, SubgroupError) as error:
        raise RequestedNotFound(str(error))


def _check_bp_group_empty(data_dict, chromosome, bp_lower, bp_upper):
    if (not data_dict) and ((bp_lower is not None) or (bp_upper is not None)):
        #TODO probably just return empty collection
        raise SubgroupError(parent="parent group: " + str(chromosome), subgroup="child group: " + str(bp_lower) + ":" + str(bp_upper))


@app.route('/chromosomes/<string:chromosome>/variants/<string:variant>')
def get_variants(chromosome, variant):
    args = request.args.to_dict()
    try:
        start, size, p_lower, p_upper, pval_interval = apiu._get_basic_arguments(args)
        study = apiu._retrieve_endpoint_arguments(args, "study_accession")
    except ValueError as error:
        raise BadUserRequest(str(error))

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_snp(snp=variant, chromosome=chromosome, start=start, size=size,
                                                     pval_interval=pval_interval, study=study)

        data_dict = apiu._get_array_to_display(datasets, variant=variant)
        params = {'variant': variant, 'chromosome': chromosome, 'p_lower': p_lower, 'p_upper': p_upper, 'study_accession': study}
        response = apiu._create_associations_response(method_name='get_variants', start=start, size=size, index_marker=index_marker,
                                                 data_dict=data_dict, params=params)

        return simplejson.dumps(OrderedDict(response), ignore_nan=True)

    except NotFoundError as error:
        raise RequestedNotFound(str(error))
    except SubgroupError:
        raise RequestedNotFound("Wrong variant id or chromosome. Chromosome: %s, variant %s" %(chromosome, variant))


def main():
    apiu._set_properties()
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
