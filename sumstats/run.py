import yaml
import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-config', help='config file', required=True)

config_files = glob.glob("/application/config/config*.yml")
print (config_files)
assert len(config_files) == 1, "We should only have one config file in the config directory!"

config_file = config_files[0]
with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


loader_type = cfg["loader"]
tsv = cfg["tsv"]
output = cfg["h5file"]
trait = cfg["trait"]
study = cfg["study"]

if loader_type == "trait":
    loader = trait_loader.Loader(tsv, output, study, trait)
    loader.load()


if loader_type == "chr":
    loader = chr_loader.Loader(tsv, output, study)
    loader.load()
