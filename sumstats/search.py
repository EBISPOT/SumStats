import yaml
import sumstats.trait.searcher as trait_searcher
import sumstats.chr.searcher as chr_searcher
import sumstats.snp.searcher as snp_searcher
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


