import sumstats.snp.search.snp_search as snps


def search_snp(snp, start, size, path=None, study=None, pval_interval=None):
    searcher = snps.SNPSearch(snp=snp, start=start, size=size, path=path)
    return searcher.search_snp(study=study, pval_interval=pval_interval)