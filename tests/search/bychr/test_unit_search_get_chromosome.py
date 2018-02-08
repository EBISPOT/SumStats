import os
import shutil

import sumstats.search as search
import tests.search.search_test_constants as search_arrays
import sumstats.chr.loader as loader
from tests.prep_tests import *
from sumstats.chr.constants import *
from tests.search.test_utils import *

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

        search_arrays.chrarray = [1 for _ in range(50)]
        h5file = self.output_location + 'file_1.h5'
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s1', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_2.h5'
        search_arrays.chrarray = [2 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s2', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_1.h5'
        search_arrays.chrarray = [1 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s3', loader=loader, test_arrays=search_arrays)
        load.load()

        h5file = self.output_location + 'file_2.h5'
        search_arrays.chrarray = [2 for _ in range(50)]
        load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s4', loader=loader, test_arrays=search_arrays)
        load.load()

        # initialize searcher with local path
        self.searcher = search.Search(path="./output")

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_nothing(self):
        assert True