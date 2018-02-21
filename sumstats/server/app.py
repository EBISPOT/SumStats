import numpy as np
import simplejson
from flask import Flask, url_for, request, abort

from urllib.parse import unquote
import sumstats.explorer as ex
import sumstats.search as search
from config import properties
from sumstats.common_constants import *
from sumstats.utils.interval import *

app = Flask(__name__)
app.url_map.strict_slashes = False


def _make_pvalue(mantissa_dset, exp_dset):
    pval_array = np.empty(len(mantissa_dset), dtype=vlen_dtype)
    for index, mantissa in enumerate(mantissa_dset):
        pval_array[index] = (str(mantissa) + "e" + str(exp_dset[index]))
    return pval_array.tolist()


def _get_array_to_display(datasets):
    if datasets is None:
        return {}
    for dset, dataset in datasets.items():
        if len(dataset) <= 0:
            return {}
        if np.issubdtype(type(dataset[0]), np.dtype):
            datasets[dset] = np.array(dataset).tolist()

    mantissa_dset = datasets.pop(MANTISSA_DSET)
    exponent_dset = datasets.pop(EXP_DSET)
    datasets[PVAL_DSET] = _make_pvalue(mantissa_dset=mantissa_dset, exp_dset=exponent_dset)

    data_dict = {}
    length = len(datasets[list(datasets.keys())[0]])
    for i in range(length):
        element_info = {}
        for dset, dataset in datasets.items():
            element_info[dset] = dataset[i]
        data_dict[i] = element_info
    return data_dict


def _retrieve_argument(args, argument_name, value_if_empty=None):
    try:
        argument = args[argument_name]
    except KeyError:
        argument = value_if_empty
    return argument


def _get_interval(value, interval):
    if value is not None:
        if ":" not in value:
            value = value + ":" + value
        return interval().set_string_tuple(value)
    return None


def _create_next_links(method_name, start, size, index_marker, size_retrieved, params={}):
    prev = max(0, start - size)
    start_new = start + index_marker

    previous_link = str(
        unquote(url_for(method_name, **params, start=prev, size=size,
                _external=True)))
    response = {
        "first": {"href": str(
            unquote(url_for(method_name, **params, start=0, size=size,
                    _external=True)))},
        "prev": {"href": previous_link},
        "self": {
            "href": str(
                unquote(url_for(method_name, **params, _external=True)))}}
    if size_retrieved == size:
        response["next"] = {"href": str(
            unquote(url_for(method_name, **params, start=start_new,
                    size=size,
                    _external=True)))}
    return response


def _explore_all_studies_for_trait(trait):
    explorer = ex.Explorer(properties.output_path)
    studies = explorer.get_list_of_studies_for_trait(trait)
    study_list = []
    for study in studies:
        sd = {"study": study, "_links": {
            "self": {"href": unquote(url_for('get_trait_studies', trait=trait, study=study, _external=True))},
            "gwas_catalog": {"href": str(properties.gwas_study_location + study)}
        }}
        study_list.append(sd)

    response = {"_embedded": {"studies": study_list}}
    return simplejson.dumps(response)


def _explore_all_traits():
    explorer = ex.Explorer(properties.output_path)
    trait_list = []
    traits = explorer.get_list_of_traits()
    for trait in traits:
        td = {"trait": trait, "_links": {
            "self": {"href": unquote(url_for('get_traits', trait=trait, _external=True))},
            "ols": {"href": str(properties.ols_terms_location + trait)}
        }}
        trait_list.append(td)

    response = {"_embedded": {"traits": trait_list}}
    return simplejson.dumps(response)


def _explore_all_chromosomes():
    chromosomes_list = []
    for chromosome in range(1, 24):
        cd = {"chromosome": chromosome, "_links": {
            "self": {"href": unquote(url_for('get_chromosomes', chromosome=chromosome, _external=True))},
        }}
        chromosomes_list.append(cd)

    response = {"_embedded": {"chromosomes": chromosomes_list}}
    return simplejson.dumps(response)


@app.route('/')
def root():
    args = {'p-value': '{lower:upper}'}
    args_chromosome = {'p-value': '{lower:upper}', 'bp': '{lower:upper}', 'study_accession': '{study_accession}'}
    args_variant = {'p-value': '{lower:upper}', 'study_accession': '{study_accession}'}
    response = {
        "_links": {
            "associations": {
                "href": unquote(url_for("get_assocs", **args, _external=True))
            },
            "traits": {
                "href": unquote(url_for("get_traits", _external=True))
            },
            "studies": {
                "href": unquote(url_for("get_studies", _external=True))
            },
            "chromosomes": {
                "href": unquote(url_for("get_chromosomes", _external=True))
            },
            "variant": {
                "href": unquote(url_for("get_variants", variant="{variant_id}", **args_variant, _external=True))
            },
            "trait": {
                "href": unquote(url_for("get_traits",
                                        trait="{trait}", **args, _external=True))
            },
            "study": {
                "href": unquote(url_for("get_trait_studies",
                                        trait="{trait}", study="{study}", **args, _external=True))
            },
            "chromosome": {
                "href": unquote(url_for("get_chromosomes",
                                        chromosome="{chromosome}", **args_chromosome, _external=True))
            }
        }
    }
    return simplejson.dumps(response)


@app.route('/associations')
def get_assocs():
    args = request.args.to_dict()
    start = int(_retrieve_argument(args, "start", 0))
    size = int(_retrieve_argument(args, "size", 20))
    pval = _retrieve_argument(args, "p-value")
    pval_interval = _get_interval(pval, FloatInterval)

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_all_assocs(start=start, size=size, pval_interval=pval_interval)

        data_dict = _get_array_to_display(datasets)
        response = {"_embedded": {"associations": data_dict}, "_links": _create_next_links(
            method_name='get_assocs', start=start, size=size, index_marker=index_marker, size_retrieved=len(data_dict),
            params={'p-value': pval}
        )}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        abort(404)


@app.route('/traits')
@app.route('/traits/<string:trait>')
def get_traits(trait=None):
    if trait is None:
        return _explore_all_traits()
    args = request.args.to_dict()
    start = int(_retrieve_argument(args, "start", 0))
    size = int(_retrieve_argument(args, "size", 20))
    pval = _retrieve_argument(args, "p-value")
    pval_interval = _get_interval(pval, FloatInterval)

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_trait(trait=trait, start=start, size=size, pval_interval=pval_interval)

        data_dict = _get_array_to_display(datasets)
        response = {"_embedded": {"trait": trait, "associations": data_dict}, "_links": _create_next_links(
            method_name='get_traits', start=start, size=size, index_marker=index_marker, size_retrieved=len(data_dict),
            params={
                'trait': trait, 'p-value': pval
            }
        )}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        abort(404)


@app.route('/studies')
def get_studies():
    explorer = ex.Explorer(properties.output_path)
    trait_studies = explorer.get_list_of_studies()
    study_list = []
    for trait_study in trait_studies:
        trait = trait_study.split(":")[0].strip(" ")
        study = trait_study.split(":")[1].strip(" ")
        sd = {"study": study, "_links": {
            "self": {"href": unquote(url_for('get_trait_studies', trait=trait, study=study, _external=True))},
            "gwas_catalog": {"href": str(properties.gwas_study_location + study)}
        }}
        study_list.append(sd)

    response = {"_embedded": {"studies": study_list}}
    return simplejson.dumps(response)


@app.route('/traits/<string:trait>/studies')
@app.route('/traits/<string:trait>/studies/<string:study>')
def get_trait_studies(trait, study=None):
    if study is None:
        return _explore_all_studies_for_trait(trait)
    args = request.args.to_dict()
    start = int(_retrieve_argument(args, "start", 0))
    size = int(_retrieve_argument(args, "size", 20))
    pval = _retrieve_argument(args, "p-value")
    pval_interval = _get_interval(pval, FloatInterval)

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_study(trait=trait, study=study,
                                                       start=start, size=size, pval_interval=pval_interval)

        data_dict = _get_array_to_display(datasets)
        response = {"_embedded": {"trait": trait, "associations": data_dict}, "_links": _create_next_links(
            method_name='get_trait_studies', start=start, size=size, index_marker=index_marker,
            size_retrieved=len(data_dict),
            params={
                'trait': trait, 'study': study, 'p-value': pval
            }
        )}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        abort(404)


@app.route('/chromosomes')
@app.route('/chromosomes/<string:chromosome>')
def get_chromosomes(chromosome=None):
    if chromosome is None:
        return _explore_all_chromosomes()
    args = request.args.to_dict()
    start = int(_retrieve_argument(args, "start", 0))
    size = int(_retrieve_argument(args, "size", 20))
    pval = _retrieve_argument(args, "p-value")
    pval_interval = _get_interval(pval, FloatInterval)
    study = _retrieve_argument(args, "study_accession")
    bp = _retrieve_argument(args, "bp")
    bp_interval = _get_interval(bp, IntInterval)

    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_chromosome(chromosome=chromosome,
                                                            start=start, size=size, study=study,
                                                            pval_interval=pval_interval, bp_interval=bp_interval)

        data_dict = _get_array_to_display(datasets)
        response = {"_embedded": {"associations": data_dict}, "_links": _create_next_links(
            method_name='get_chromosomes', start=start, size=size, index_marker=index_marker,
            size_retrieved=len(data_dict),
            params={
                'chromosome': chromosome, 'p-value': pval, 'bp': bp, 'study_accession': study
            }
        )}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        abort(404)


@app.route('/variants/<string:variant>')
def get_variants(variant):
    args = request.args.to_dict()
    start = int(_retrieve_argument(args, "start", 0))
    size = int(_retrieve_argument(args, "size", 20))
    pval = _retrieve_argument(args, "p-value")
    pval_interval = _get_interval(pval, FloatInterval)
    study = _retrieve_argument(args, "study_accession")
    
    searcher = search.Search(properties.output_path)

    try:
        datasets, index_marker = searcher.search_snp(snp=variant,
                                                     start=start, size=size, 
                                                     pval_interval=pval_interval, study=study)

        data_dict = _get_array_to_display(datasets)
        response = {"_embedded": {"associations": data_dict}, "_links": _create_next_links(
            method_name='get_variants', start=start, size=size, index_marker=index_marker,
            size_retrieved=len(data_dict),
            params={
                'variant': variant, 'p-value': pval, 'study_accession': study
            }
        )}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        abort(404)


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
