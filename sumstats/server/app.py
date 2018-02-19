import simplejson
from flask import Flask, url_for, request

import sumstats.explorer as ex
import sumstats.search as search
import numpy as np

app = Flask(__name__)


def generate(array):
    for row in array:
        yield ",".join(row) + "\n"


def get_array_to_display(datasets):
    if datasets is None:
        return {}
    for dset, dataset in datasets.items():
        if len(dataset) <= 0:
            return {}
        if np.issubdtype(type(dataset[0]), np.dtype):
            datasets[dset] = np.array(dataset).tolist()

    data_dict = {}
    length = len(datasets[list(datasets.keys())[0]])
    for i in range(length):
        element_info = {}
        for dset, dataset in datasets.items():
            element_info[dset] = dataset[i]
        data_dict[i] = element_info
    return data_dict


def retrieve_argument(args, argument_name, value_if_empty=None):
    try:
        argument = args[argument_name]
    except KeyError:
        argument = value_if_empty
    return argument


def get_previous(start, size):
    return start - size


@app.route("/")
def hello():
    explorer = ex.Explorer()
    studies = explorer.get_list_of_studies()
    loaded = "<ul>"
    for elements in studies:
        print(elements)
        loaded = loaded + "<li>" + elements
    loaded = loaded + "</ul>"

    query_trait = str(url_for('get_assocs', trait="trait", _external=True))
    query_study = str(url_for('get_assocs', trait="trait", study="study", _external=True))
    query_chromosome = str(url_for('get_assocs', chr="chr", _external=True))
    query_variant = str(url_for('get_assocs', variant="variant", _external=True))

    query_trait_size = str(url_for('get_assocs', trait="trait", start=0, size=20, _external=True))
    query_study_size = str(url_for('get_assocs', trait="trait", study="study", start=0, size=20, _external=True))
    query_chromosome_size = str(url_for('get_assocs', chr="chr", start=0, size=20, _external=True))
    query_variant_size = str(url_for('get_assocs', variant="variant", start=0, size=20, _external=True))

    return "<!DOCTYPE html> \
            <html lang=\"en\"> \
            <head> \
            <title>Summary Statistics</title> \
            <meta charset=\"utf-8\"> \
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> \
            <link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css\"> \
            <script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.2.0/jquery.min.js\"></script> \
            <script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js\"></script> \
            </head> \
            <body>" \
           "<div class=\"container\"> <h1 style=\"color:red;\">This is a <i>very</i> first prototype of the API and " \
           "it will " \
           "change</h1><h3>Summary Statistics</h3><h4> Below you can see the endpoint to the " \
           "query API and what is " \
           "currently loaded.</h4>" \
           "<p>Query for trait: <a href=" + query_trait_size + " target=_blank>" + query_trait + "</a></p>" + \
           "<p>Query for study: <a href=" + query_study_size + " target=_blank>" + query_study + "</a></p>" + \
           "<p>Query for chromosome: <a href=" + query_chromosome_size + " target=_blank>" + query_chromosome + "</a></p>" + \
           "<p>Query for variant: <a href=" + query_variant_size + " target=_blank>" + query_variant + "</a></p>" + \
           "<p><b>Currently loaded:</b></p>" + \
           loaded + \
           "</div></body></html> "


@app.route("/associations")
def get_assocs():
    args = request.args.to_dict()
    trait = retrieve_argument(args, "trait")
    study = retrieve_argument(args, "study")
    chromosome = retrieve_argument(args, "chr")
    if chromosome is not None:
        chromosome = int(chromosome)
    variant = retrieve_argument(args, "variant")
    start = int(retrieve_argument(args, "start", 0))
    size = int(retrieve_argument(args, "size", 20))

    searcher = search.Search()

    try:
        if trait is not None:
            if study is not None:
                datasets, index_marker = searcher.search_study(trait=trait, study=study, start=start, size=size)
            else:
                datasets, index_marker = searcher.search_trait(trait=trait, start=start, size=size)
        elif chromosome is not None:
            datasets, index_marker = searcher.search_chromosome(chromosome=chromosome, start=start, size=size)
        elif variant is not None:
            datasets, index_marker = searcher.search_snp(snp=variant, start=start, size=size)
        else:
            datasets, index_marker = searcher.search_all_assocs(start=start, size=size)

        data_dict = get_array_to_display(datasets)
        response = {"_embedded": {"trait": trait, "data": data_dict}}

        prev = get_previous(start, size)
        start_new = start + index_marker

        if prev >= 0:
            previous_link = str(
                url_for('get_assocs', trait=trait, study=study, chr=chromosome, variant=variant, start=prev, size=size,
                        _external=True))
        else:
            previous_link = str(
                url_for('get_assocs', trait=trait, study=study, chr=chromosome, variant=variant, start=0, size=size,
                        _external=True))

        response["_links"] = {
            "first": {"href": str(
                url_for('get_assocs', trait=trait, study=study, chr=chromosome, variant=variant, start=0, size=size,
                        _external=True))},
            "next": {"href": str(
                url_for('get_assocs', trait=trait, study=study, chr=chromosome, variant=variant, start=start_new,
                        size=size,
                        _external=True))},
            "prev": {"href": previous_link},
            "self": {
                "href": str(
                    url_for('get_assocs', trait=trait, study=study, chr=chromosome, variant=variant, _external=True))}}

        return simplejson.dumps(response, ignore_nan=True)

    except ValueError:
        return "Trait not in file: " + trait


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
