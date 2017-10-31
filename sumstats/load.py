import sumstats.trait.loader as trait_loader
import sumstats.chr.loader as chr_loader
import sumstats.snp.loader as snp_loader
import sumstats.utils.argument_utils as au

args = au.load_argument_parser()

loader_type = args.loader
if loader_type is None:
    raise ValueError("You need to specify a loader: [trait|chr|snp]")

tsv = args.tsv
trait = args.trait
study = args.study
output_path = args.output_path
input_path = args.input_path
chr = args.chr

if output_path is None:
    print("Setting default location for output files")
    output_path = "."

if input_path is None:
    print("Setting default location for input files")
    output_path = "."

output_path = output_path + "/output"
input_path = input_path + "/toload"
to_load = input_path + "/" + tsv

if loader_type == "trait":
    to_store = output_path + "/bytrait/file_" + trait + ".h5"
    loader = trait_loader.Loader(to_load, to_store, study, trait)
    loader.load()
    print("Load complete!")

if loader_type == "chr":
    if chr is None:
        raise ValueError("You need to specify the chromosome that is being loaded with the chr loader!")

    to_store = output_path + "/bychr/file_" + str(chr) + ".h5"
    loader = chr_loader.Loader(to_load, to_store, study)
    loader.load()
    print("Load complete!")

if loader_type == "snp":
    if chr is None:
        raise ValueError("You need to specify the chromosome that the SNP belongs to with the snp loader!")

    to_store = output_path + "/bysnp/file_" + str(chr) + ".h5"
    loader = snp_loader.Loader(to_load, to_store, study)
    loader.load()
    print("Load complete!")
