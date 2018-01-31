from sumstats.common_constants import *


def assert_number_of_times_study_is_in_datasets(datasets, study, size):
    study_sum = len([s for s in datasets[STUDY_DSET] if s == study])
    assert study_sum == size


def assert_datasets_have_size(datasets, TO_QUERY_DSETS, size):
    for name in TO_QUERY_DSETS:
        assert len(datasets[name]) == size


def assert_only_list_of_studies_returned(datasets, studies):
    unique_studies = set(datasets[STUDY_DSET])
    assert len(unique_studies) == len(studies)

    for study in unique_studies:
        assert study in studies