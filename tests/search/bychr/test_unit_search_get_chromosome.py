import os
import shutil

import sumstats.search as search
import tests.search.search_test_constants as search_arrays
import sumstats.chr.loader as loader
from tests.prep_tests import *
from sumstats.chr.constants import *
from tests.search.test_utils import *
import sumstats.utils.utils as utils


class TestLoader(object):

    output_location = './output/bychr/'
    file = None
    start = 0
    size = 20

    def setup_method(self, method):
        # output is always stored under a directory called: 'output'
        os.makedirs('./output/bychr')

        # loaded s1/t1 -> 50 associations
        # loaded s2/t1 -> 50 associations
        # loaded s3/t2 -> 50 associations
        # loaded s4/t2 -> 50 associations
        # total associations loaded : 200

        # studies s1 and s3 have the same chromosome (1)
        # studies s2 and s4 have the same chromosome (2)

        # there will be 2 distinct bp ranges : 0-1200000 / 48500000-49200000
        # each range for one chromosome has 50 elements in it (25 per study, 2 studies per chromosome)

        search_arrays.chrarray = [1 for _ in range(50)]

        search_arrays.bparray = [1120431 for _ in range(25)]
        search_arrays.bparray.extend([48480252 for _ in range(15)])
        search_arrays.bparray.extend([49129966 for _ in range(10)])

        h5file = self.output_location + 'file_1.h5'
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s1', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_2.h5'
        search_arrays.chrarray = [2 for _ in range(50)]
        search_arrays.snpsarray = ['rs' + str(i) for i in range(50, 100)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s2', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_1.h5'
        search_arrays.chrarray = [1 for _ in range(50)]
        search_arrays.snpsarray = ['rs' + str(i) for i in range(100, 150)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s3', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_2.h5'
        search_arrays.chrarray = [2 for _ in range(50)]
        search_arrays.snpsarray = ['rs' + str(i) for i in range(150, 200)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s4', loader=loader, test_arrays=search_arrays)
        load.load()

        # initialize searcher with local path
        self.searcher = search.Search(path="./output")

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_get_chromosome_1_0_20(self):
        start = 0
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_in_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_20_40(self):
        start = 20
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_40_60(self):
        start = 40
        size = 20
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)
        assert_studies_from_list(datasets, ['s1', 's3'])
        assert index_marker == 20
        assert len(set(datasets[SNP_DSET])) == len(datasets[SNP_DSET])

    def test_get_chromosome_1_loop_through_size_5(self):
        start = 0
        size = 5

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 5)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 21
        # 100 unique variants
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chromosome_1_loop_through_size_20(self):
        start = 0
        size = 20

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 20)

            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 6
        # 100 unique variants
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])

    def test_get_chromosome_1_loop_through_size_50(self):
        start = 0
        size = 50

        looped_through = 1
        d = utils.create_dictionary_of_empty_dsets(TO_QUERY_DSETS)
        datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
        d = utils.extend_dsets_with_subset(d, datasets)
        while len(datasets[REFERENCE_DSET]) > 0:
            assert_studies_in_list(datasets, ['s1', 's3'])
            assert_datasets_have_size(datasets, TO_QUERY_DSETS, 50)
            start = start + index_marker
            datasets, index_marker = self.searcher.search_chromosome(chromosome=1, start=start, size=size)
            d = utils.extend_dsets_with_subset(d, datasets)
            looped_through += 1

        assert looped_through == 3
        assert len(set(d[SNP_DSET])) == len(d[SNP_DSET])