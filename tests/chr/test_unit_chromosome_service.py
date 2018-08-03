import os
import pytest

from sumstats.errors.error_classes import *
import sumstats.chr.loader as loader
from sumstats.chr.search.access.chromosome_service import *
from tests.prep_tests import *
from sumstats.utils.interval import *


class TestUnitChromosomeService(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self):

        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        # pvalsarray = ["0.4865", "0.4314", "0.5986", "0.07057"]
        # loading 3 ranges 1200000 with 2 elements, 49129966 with one element, and  49200000 with one element
        # loading 3 times, once per study

        # requesting only lower range should bring back 6 elements (2 elements times 3 studies)
        # requesting only one of the upper ranges should bring back 3 elements
        # requesting both the 2 upper ranges should bring back 6 elements

        # requesting for only 1 specific bp location should return 3 elements, one for each study

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        self.start = 0
        self.size = 20
        self.service = ChromosomeService(self.h5file)

    def teardown_method(self):
        os.remove(self.h5file)

    def test_query_for_chromosome(self):
        self.service.query(2, self.start, self.size)
        datasets = self.service.get_result()

        assert len(datasets[BP_DSET]) == 6
        assert len(datasets[SNP_DSET]) == 6

    def test_query_non_existing_chromosome_raises_error(self):
        with pytest.raises(NotFoundError):
            self.service.query(24, self.start, self.size)

    def test_apply_pval_restrictions(self):
        self.service.query(2, self.start, self.size)
        pval_interval = FloatInterval().set_tuple(0.5, None)
        self.service.apply_restrictions(pval_interval=pval_interval)
        datasets = self.service.get_result()

        assert len(datasets[REFERENCE_DSET]) == 3

    def test_chromosome_size(self):
        # chromosome 1 has 2 ranges loaded
        # these ranges are loaded 3 times (once for each study)
        chromosome_size = self.service.get_chromosome_size(1)
        assert chromosome_size == 6

