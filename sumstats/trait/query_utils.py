from sumstats.trait.constants import *
from sumstats.utils.utils import *
import sumstats.utils.group as gu


def get_dsets_from_file(f):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    for trait, trait_group in f.items():
        name_to_datastet_for_trait = get_dsets_from_trait_group(trait_group)
        for dset_name, dataset in name_to_dataset.items():
            dataset.extend(name_to_datastet_for_trait[dset_name])

    return name_to_dataset


def get_dsets_from_trait_group(trait_group):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

    for study, study_group in trait_group.items():
        name_to_dataset_for_study = get_dsets_from_group(study, study_group)
        for dset_name, dataset in name_to_dataset.items():
            dataset.extend(name_to_dataset_for_study[dset_name])
    return name_to_dataset


def get_dsets_from_group(study, study_group):
    name_to_dataset = create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
    return gu.extend_dsets_for_group_missing(missing_value=study, group=study_group,
                                             name_to_dataset=name_to_dataset,
                                             missing_dset=STUDY_DSET,
                                             existing_dset=SNP_DSET)