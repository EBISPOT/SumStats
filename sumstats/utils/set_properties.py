import json
from config import properties


def set_properties(config):

    if config is not None:
        with open(config) as config:
            props = json.load(config)
            properties.output_path = props["output_path"]
            properties.gwas_study_location = props["gwas_study_location"]
            properties.input_path = props["input_path"]
            properties.ols_terms_location = props["ols_terms_location"]
            properties.logging_path = props["logging_path"]
            properties.LOG_LEVEL = props["LOG_LEVEL"]
