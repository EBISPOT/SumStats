import os
import shutil

import sumstats.controller as search
import tests.search.search_test_constants as search_arrays
import sumstats.snp.loader as loader
from tests.prep_tests import *
from sumstats.snp.constants import *
from tests.search.test_utils import *
import sumstats.utils.dataset_utils as utils
from sumstats.errors.error_classes import *
import pytest
from config import properties


@pytest.yield_fixture(scope="session", autouse=True)
def load_studies(request):
    os.makedirs('./outputsnp/bysnp/1')
    output_location = './outputsnp/bysnp/'

    # loaded 2 variants for 5 studies
    # studies s1, s3 and s5 have p-value: 0.01
    # studies s2 and s4 have p-value: 0.1

    search_arrays.chrarray = [1 for _ in range(1, 3)]
    search_arrays.snpsarray = ['rs' + str(i) for i in range(1, 3)]
    h5file = output_location + '/1/file_1.h5'

    search_arrays.pvalsarray = ["0.01" for _ in range(1, 3)]
    load = prepare_load_object_with_study(h5file=h5file, study='s1', loader=loader, test_arrays=search_arrays)
    load.load()

    search_arrays.pvalsarray = ["0.1" for _ in range(1, 3)]
    load = prepare_load_object_with_study(h5file=h5file, study='s2', loader=loader, test_arrays=search_arrays)
    load.load()

    search_arrays.pvalsarray = ["0.01" for _ in range(1, 3)]
    load = prepare_load_object_with_study(h5file=h5file, study='s3', loader=loader, test_arrays=search_arrays)
    load.load()

    search_arrays.pvalsarray = ["0.1" for _ in range(1, 3)]
    load = prepare_load_object_with_study(h5file=h5file, study='s4', loader=loader, test_arrays=search_arrays)
    load.load()

    search_arrays.pvalsarray = ["0.01" for _ in range(1, 3)]
    load = prepare_load_object_with_study(h5file=h5file, study='s5', loader=loader, test_arrays=search_arrays)
    load.load()

    request.addfinalizer(remove_dir)


def remove_dir():
    shutil.rmtree('./outputsnp')


class TestLoader(object):

    file = None
    start = 0
    size = 20

    def setup_method(self):
        # initialize searcher with local path
        properties.h5files_path = "./outputsnp"
        self.searcher = search.Search(properties)

    def test_get_snp(self):
        start = 0
        size = 20

        datasets, index_marker = self.searcher.search_snp(snp='rs1', start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
        assert len(set(datasets[STUDY_DSET])) == len(datasets[STUDY_DSET]) == 5
        # max snp group size
        assert index_marker == 5

    def test_get_snp_for_wrong_chromosome_raises_error(self):
        with pytest.raises(NotFoundError):
            self.searcher.search_snp(snp='rs1', chromosome=2, start=0, size=20)

    def test_get_unexisting_snp_raises_error(self):
        with pytest.raises(NotFoundError):
            self.searcher.search_snp(snp='rs12345', start=0, size=20)

    def test_get_snp_loop_through_size_5(self):
        start = 0
        size = 5
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        datasets, index_marker = self.searcher.search_snp(snp='rs2', start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)

        while len(datasets[REFERENCE_DSET]) > 0:
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_snp(snp='rs2', start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)

        assert len(d[REFERENCE_DSET]) == 5

    def test_get_snp_loop_through_size_1(self):
        start = 0
        size = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)

        datasets, index_marker = self.searcher.search_snp(snp='rs2', start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)

        while len(datasets[REFERENCE_DSET]) > 0:
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 1)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_snp(snp='rs2', start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)

        assert len(d[REFERENCE_DSET]) == 5

