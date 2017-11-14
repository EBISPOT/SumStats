import json
from flask import Flask, url_for, Response, request

import sumstats.explorer as ex
import sumstats.load as ld
import sumstats.search as search
import os
import numpy as np

app = Flask(__name__)


def generate(array):
    for row in array:
        yield ",".join(row) + "\n"


def get_array_to_display(name_to_dataset, start=None, size=None):
    for dset, dataset in name_to_dataset.items():
        end = min(len(dataset), (start + size))
        if np.issubdtype(type(dataset[0]), np.dtype):
            name_to_dataset[dset] = np.array(dataset[start:end]).tolist()
        else:
            name_to_dataset[dset] = dataset[start:end]
    return name_to_dataset


@app.route("/")
def hello():
    explorer = ex.Explorer()
    traits = explorer.get_list_of_traits()
    studies = explorer.get_list_of_studies()
    trait = str(url_for('get_trait', trait="foo", start=0, size=20, _external=True))
    study = str(url_for('get_study', trait="foo", study="bar", _external=True))
    return "<html> <ul> Select from: <li>get trait from: <a href=" + trait + " target=_blank>" + trait + "</a></li>" + \
           "<li>get study from: <a href=" + study + " target=_blank>" + study + "</a></li>" +\
           "<p> Loaded traits: " + str(traits) + "</p>" + \
           "<p> Loaded studies: " + str(studies) + "</p>" + \
           "</html>"


@app.route("/trait")
def get_trait():
    searcher = search.Search()

    args = request.args.to_dict()
    trait = args["trait"]
    try:
        start = args["start"]
        start = int(start)
    except KeyError:
        start = 0
    try:
        size = args["size"]
        size = int(size)
    except KeyError:
        size = 20

    try:
        name_to_dataset = searcher.search_trait(trait)
        name_to_dataset = get_array_to_display(name_to_dataset, start, size)
        name_to_dataset["trait"] = trait
        response = {"_embedded" : name_to_dataset}

        prev = start - size
        start_new = start + size
        if prev >= 0:
            previous_link = str(url_for('get_trait', trait=trait, start=prev, size=size, _external=True))
        else:
            previous_link = str(url_for('get_trait', trait=trait, start=0, size=size, _external=True))

        response["_links"] = {"first": {"href" : str(url_for('get_trait', trait=trait, start=0, size=size, _external=True))},
                              "next" : {"href" : str(url_for('get_trait', trait=trait, start=start_new, size=size, _external=True))},
                              "prev" : {"href" : previous_link},
                              "self" : {"href" : str(url_for('get_trait', trait=trait, _external=True))}}

        return json.dumps(response)
    except ValueError:
        return "Trait not in file: " + trait


@app.route("/trait/study")
def get_study():
    searcher = search.Search()

    args = request.args.to_dict()
    trait = args["trait"]
    study = args["study"]

    try:
        name_to_dataset = searcher.search_study(trait, study)
        name_to_dataset = get_array_to_display(name_to_dataset)
        return json.dumps(name_to_dataset)
    except ValueError:
        return "Bad trait/study combination: " + trait + "/" + study


if __name__ == '__main__':
    print("NAME", __name__)
    app.run()
