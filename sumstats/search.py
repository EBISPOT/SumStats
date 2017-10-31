import sumstats.trait.searcher as trait_searcher
import sumstats.chr.searcher as chr_searcher
import sumstats.snp.searcher as snp_searcher
import sumstats.utils.argument_utils as au
import os.path


args = au.search_argument_parser()

trait, study, chr, bp_interval, snp, pval_interval = au.convert_search_args(args)
path = args.path
if path is None:
    print("Setting default location for output files")
    path = "."


output_path = path + "/output"

result = None
searcher = None

if trait is not None:
    h5file = output_path + "/bytrait/file_" + trait + ".h5"
    if os.path.isfile(h5file):
        searcher = trait_searcher.Search(h5file)
        if study is not None:
            searcher.query_for_study(trait, study)
        else:
            searcher.query_for_trait(trait)

        searcher.apply_restrictions(snp=snp, chr=chr, pval_interval=pval_interval, bp_interval=bp_interval)
        result = searcher.get_result()

elif chr is not None:
    h5file = output_path + "/bychr/file_" + str(chr) + ".h5"
    if os.path.isfile(h5file):
        searcher = chr_searcher.Search(h5file)
        if bp_interval is not None:
            searcher.query_chr_for_block_range(chr, bp_interval)
        else:
            searcher.query_for_chromosome(chr)
        searcher.apply_restrictions(study=study, pval_interval=pval_interval)
        result = searcher.get_result()

elif snp is not None:
    for chr in range(1, 23):
        h5file = output_path + "/bysnp/file_" + str(chr) + ".h5"
        if os.path.isfile(h5file):
            searcher = snp_searcher.Search(h5file)
            if searcher.snp_in_file(snp):
                searcher.query_for_snp(snp)
                searcher.apply_restrictions(study=study, pval_interval=pval_interval)
                result = searcher.get_result()
else:
    raise ValueError("Input is wrong!")


if result is not None:
    for name, dataset in result.items():
        print(name, dataset)
else:
    print("Result is empty!")

