import json
from flask import Flask, url_for, Response, request

from sumstats.trait.searcher import Search
import os
import numpy as np

app = Flask(__name__)

H5FILE_PATH = "/application/files/h5files/"
def generate(array):
    for row in array:
        yield ",".join(row) + "\n"


def get_array_to_display(name_to_dataset):
    for dset in name_to_dataset:
        if np.issubdtype(name_to_dataset[dset].dtype, np.string_):
            name_to_dataset[dset] = np.array(name_to_dataset[dset], dtype=str)
        else:
            name_to_dataset[dset] = name_to_dataset[dset]
    array = None
    header = np.array([], dtype=None)
    for dset in name_to_dataset:
        header = np.append(header, dset)
        if array is None:
            array = name_to_dataset[dset]
        else:
            array = np.column_stack((array, name_to_dataset[dset]))

    return np.row_stack((header, array))


@app.route("/")
def hello():
    trait = str(url_for('get_trait', trait="foo", _external=True))
    study = str(url_for('get_study', trait="foo", study="bar", _external=True))
    return "<html> <ul> Select from: <li>get trait from: <a href=" + trait + " target=_blank>" + trait + "</a></li>" + \
           "<li>get study from: <a href=" + study + " target=_blank>" + study + "</li>" +\
           "</html>"


@app.route("/trait")
def get_trait():
    path = os.path.abspath(H5FILE_PATH + "test.h5")
    searcher = Search(path)

    args = request.args.to_dict()
    trait = args["trait"]

    try:
        name_to_dataset = searcher.query_for_trait(trait)
        array = get_array_to_display(name_to_dataset)

        return Response(generate(array), mimetype="text/csv")
    except ValueError:
        return "Trait not in file: " + trait


@app.route("/trait/study")
def get_study():
    path = os.path.abspath(H5FILE_PATH + "test.h5")
    searcher = Search(path)

    args = request.args.to_dict()
    trait = args["trait"]
    study = args["study"]

    try:
        name_to_dataset = searcher.query_for_study(trait, study)
        array = get_array_to_display(name_to_dataset)

        return Response(generate(array), mimetype="text/csv")
    except ValueError:
        return "Bad trait/study combination: " + trait + "/" + study


if __name__ == '__main__':
    print("NAME", __name__)
    app.run()
