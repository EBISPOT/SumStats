import sumstats.trait.search.association_search as assoc_search
import sumstats.trait.search.trait_search as ts
import sumstats.trait.search.study_search as ss


def search_all_assocs(start, size, pval_interval=None, path=None):
    search_all = assoc_search.AssociationSearch(start=start, size=size, path=path)
    return search_all.get_all_associations(pval_interval)


def search_trait(trait, start, size, pval_interval=None, path=None):
    search_trait = ts.TraitSearch(trait=trait, start=start, size=size, path=path)
    return search_trait.search_trait(pval_interval)


def search_study(trait, study, start, size, pval_interval=None, path=None):
    search_study = ss.StudySearch(trait=trait, start=start, size=size, path=path)
    return search_study.search_study(study=study, pval_interval=pval_interval)
