from sumstats.common_constants import *


def assert_number_of_times_study_is_in_datasets(datasets, study, size):
    study_sum = len([s for s in datasets[STUDY_DSET] if 'GCST' + str(s) == study])
    assert study_sum == size


def assert_datasets_have_size(datasets, TO_QUERY_DSETS, size):
    for name in TO_QUERY_DSETS:
        if datasets:
            assert len(datasets[name]) == size
        else:
            assert 0 == size


def assert_studies_from_list(datasets, studies):
    studies_with_gcst = ['GCST' + str(study) for study in datasets[STUDY_DSET]]
    unique_studies = set(studies_with_gcst)
    assert len(unique_studies) == len(studies)

    for study in unique_studies:
        assert study in studies


def assert_studies_in_list(datasets, studies):
    unique_studies = set(datasets[STUDY_DSET])
    found = False
    print(len(unique_studies))
    if len(unique_studies) == 1:
        for study in studies:
            if study in unique_studies:
                found = True
        assert found
    else:
        assert_studies_from_list(datasets, studies)