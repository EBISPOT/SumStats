import sumstats.chr.search.chromosome_search as cs


def search_chromosome(chromosome, start, size, path=None, bp_interval=None, study=None, pval_interval=None):
    searcher = cs.ChromosomeSearch(chromosome=chromosome, start=start, size=size, path=path)
    if bp_interval is None:
        return searcher.search_chromosome(study=study, pval_interval=pval_interval)
    else:
        return searcher.search_chromosome_block(bp_interval=bp_interval, study=study, pval_interval=pval_interval)