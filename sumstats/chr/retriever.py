import sumstats.chr.search.chromosome_search as cs
import sumstats.chr.search.block_search as bls


def search_chromosome(chromosome, start, size, properties=None, bp_interval=None, study=None, pval_interval=None, snp=None):
    if bp_interval is None:
        searcher = cs.ChromosomeSearch(chromosome=chromosome, start=start, size=size, config_properties=properties)
        return searcher.search_chromosome(study=study, pval_interval=pval_interval)
    else:
        searcher = bls.BlockSearch(chromosome=chromosome, start=start, size=size, config_properties=properties)
        return searcher.search_chromosome_block(bp_interval=bp_interval, study=study, pval_interval=pval_interval, snp=snp)