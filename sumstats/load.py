import yaml
import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-config', help='config file location', required=False)
args = parser.parse_args()
if args.config is None:
    print("Setting default location for configuration file")
    config_location = "/application/config"
else:
    config_location = args.config

config_files = glob.glob(config_location + "/config*.yml")
print (config_files)
assert len(config_files) == 1, "We should have exactly one config file in the config directory!"

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
    print("Load complete!")

if loader_type == "chr":
    loader = chr_loader.Loader(tsv, output, study)
    loader.load()
    print("Load complete!")

if loader_type == "snp":
    loader = snp_loader.Loader(tsv, output, study)
    loader.load()
    print("Load complete!")
