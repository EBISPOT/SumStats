import os
import shutil

import sumstats.controller as search
import tests.search.search_test_constants as search_arrays
import sumstats.trait.loader as loader
import sumstats.utils.utils as utils
from tests.prep_tests import *
from sumstats.trait.constants import *
from tests.search.test_utils import *
import pytest


@pytest.yield_fixture(scope="session", autouse=True)
def load_studies(request):
    os.makedirs('./outputtrait/bytrait')
    output_location = './outputtrait/bytrait/'

    # loaded s1/t1 -> 50 associations
    # loaded s2/t1 -> 50 associations
    # loaded s3/t2 -> 50 associations
    # loaded s4/t2 -> 50 associations
    # total associations loaded : 200

    search_arrays.chrarray = [1 for _ in range(50)]
    search_arrays.pvalsarray = ["0.00001" for _ in range(25)]
    search_arrays.pvalsarray.extend(["0.0001" for _ in range(25, 50)])
    search_arrays.snpsarray = ['rs' + str(i) for i in range(50)]
    h5file = output_location + 'file_t1.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s1', trait='t1', loader=loader,
                                                    test_arrays=search_arrays)
    load.load()

    search_arrays.chrarray = [2 for _ in range(50)]
    search_arrays.pvalsarray = ["0.001" for _ in range(50)]
    search_arrays.snpsarray = ['rs' + str(i) for i in range(50, 100)]
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s2', trait='t1', loader=loader,
                                                    test_arrays=search_arrays)
    load.load()

    h5file = output_location + 'file_t2.h5'
    search_arrays.chrarray = [1 for _ in range(50)]
    search_arrays.pvalsarray = ["0.05" for _ in range(50)]
    search_arrays.snpsarray = ['rs' + str(i) for i in range(100, 150)]
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s3', trait='t2', loader=loader,
                                                    test_arrays=search_arrays)
    load.load()

    search_arrays.chrarray = [2 for _ in range(50)]
    search_arrays.pvalsarray = ["0.1" for _ in range(50)]
    search_arrays.snpsarray = ['rs' + str(i) for i in range(150, 200)]
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s4', trait='t2', loader=loader,
                                                    test_arrays=search_arrays)
    load.load()

    h5file = output_location + 'file_t3.h5'
    search_arrays.chrarray = [2 for _ in range(50)]
    search_arrays.pvalsarray = ["0.0000000001" for _ in range(15)]
    search_arrays.pvalsarray.extend(["0.000001" for _ in range(15, 35)])
    search_arrays.pvalsarray.extend(["0.0000000001" for _ in range(35, 40)])
    search_arrays.pvalsarray.extend(["0.000001" for _ in range(40, 50)])
    search_arrays.snpsarray = ['rs' + str(i) for i in range(200, 250)]
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s5', trait='t3', loader=loader,
                                                    test_arrays=search_arrays)
    load.load()

    request.addfinalizer(remove_dir)


def remove_dir():
    shutil.rmtree('./outputtrait')


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        self.searcher = search.Search(path="./outputtrait")

    def test_size_start_0_size_50_returns_only_first_and_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=50)
        assert_studies_from_list(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_size_51_returns_first_and_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=51)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS,51)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 1)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_start_0_size_0(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=0)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_start_50_size_50_returns_only_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=50, size=50)
        assert_studies_from_list(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_start_49_size_51_returns_first_and_second_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=49, size=51)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 51)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 1)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_start_100_size_100_returns_third_and_fourth_study(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=100, size=100)
        assert_studies_from_list(datasets, ['s3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 100)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=200)
        assert_studies_from_list(datasets, ['s1', 's2', 's3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 200)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_size_bigger_than_existing_data(self):
        datasets, index_marker = self.searcher.search_all_assocs(start=0, size=220)
        assert_studies_from_list(datasets, ['s1', 's2', 's3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 200)
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 50)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 50)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_loop_through_size_20(self):
        start = 0
        size = 20

        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            if start + index_marker >= 240:
                assert_datasets_have_size(datasets, TO_QUERY_DSETS, 10)
            else:
                assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)

        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_all_0_to_20(self):
        start = 0
        size = 20
        # first 20 of study s1
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_20_to_40(self):
        start = 20
        size = 20
        # 20-40 of study s1
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s1'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_40_to_60(self):
        start = 40
        size = 20
        # 40-50 of study s1 and first 10 (remaining) of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s1', 's2'])
        assert_number_of_times_study_is_in_datasets(datasets, 's1', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's2', 10)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_60_to_80(self):
        start = 60
        size = 20
        # 10-30 of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_80_to_100(self):
        start = 80
        size = 20
        # 30-50 of study s2
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s2'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_100_to_120(self):
        start = 100
        size = 20
        # first 20 of study s3
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s3'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_120_to_140(self):
        start = 120
        size = 20
        # 20 - 40 of study s3
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s3'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_140_to_160(self):
        start = 140
        size = 20
        # 40 - 50 of study s3 and first 10 if study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s3', 's4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_number_of_times_study_is_in_datasets(datasets, 's3', 10)
        assert_number_of_times_study_is_in_datasets(datasets, 's4', 10)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_160_to_180(self):
        start = 160
        size = 20
        # 10 - 30 of study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_all_180_to_200(self):
        start = 180
        size = 20
        # 30 - 50 of study s4
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_studies_from_list(datasets, ['s4'])
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_out_of_bounds(self):
        start = 250
        size = 20
        # empty
        datasets, index_marker = self.searcher.search_all_assocs(start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 0)
