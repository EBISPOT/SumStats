import sumstats.chr.search.association_search as assoc_search



def search_all_assocs(start, size, pval_interval=None, properties=None, study=None, trait=None,
                      chromosome=None, bp_interval=None, tissue=None, snp=None):
    search_all = assoc_search.AssociationSearch(start=start, size=size, pval_interval=pval_interval, trait=trait,
                                                config_properties=properties, study=study, chromosome=chromosome,
                                                bp_interval=bp_interval, tissue=tissue, snp=snp)
    return search_all.search_associations()

