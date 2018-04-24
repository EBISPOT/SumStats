import json
from config import properties
import argparse


def set_properties(argparser=None):
    if argparser is None:
        argparser = argparse.ArgumentParser()
    argparser.add_argument('-config', help='The configuration file to use instead of default')
    args = argparser.parse_args()

    if args.config is not None:
        set_config_properties(config=args.config)


def set_config_properties(config):
    with open(config) as config:
        props = json.load(config)
        properties.h5files_path = props["h5files_path"]
        properties.gwas_study_location = props["gwas_study_location"]
        properties.tsvfiles_path = props["tsvfiles_path"]
        properties.ols_terms_location = props["ols_terms_location"]
        properties.trait_dir = props["trait_dir"]
        properties.chr_dir = props["chr_dir"]
        properties.snp_dir = props["snp_dir"]
        properties.logging_path = props["logging_path"]
        properties.port = props["port"]
        properties.bp_step = props["bp_step"]
        properties.LOG_LEVEL = props["LOG_LEVEL"]


def get_properties(config_properties=None):
    if config_properties is not None:
        return config_properties
    return properties


def get_search_path(config_properties):
    if config_properties is not None:
        path = config_properties.h5files_path
    else:
        path = properties.h5files_path
    if path is None:
        path = "/output"
    return path