import os

import sumstats.snp.loader as loader
from sumstats.snp.search.access.service import Service
from tests.prep_tests import *
from sumstats.errors.error_classes import *
import pytest


class TestUnitSearcher(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        self.start = 0
        self.size = 20
        self.query = Service(self.h5file)
        self.studies = ['PM001', 'PM002', 'PM003']
        self.existing_snp = 'rs7085086'
        self.non_existing_snp = 'rs1234567'

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_snp(self):
        self.query.query_for_snp(snp=self.existing_snp, start=self.start, size=self.size)
        datasets = self.query.get_result()

        assert isinstance(datasets, dict)

        for dset_name in datasets:
            assert len(datasets[dset_name]) == 3

        assert len(set(datasets[CHR_DSET])) == 1
        assert set(datasets[CHR_DSET]).pop() == 2

    def test_query_for_non_existing_snp_raises_error(self):
        with pytest.raises(SubgroupError):
            self.query.query_for_snp(snp=self.non_existing_snp, start=self.start, size=self.size)

    def test_get_snp_size_raises_error_for_not_existing_snp(self):
        with pytest.raises(SubgroupError):
            self.query.get_snp_size(self.non_existing_snp)

    def test_get_snp_size(self):
        snp_size = self.query.get_snp_size(self.existing_snp)
        assert snp_size == len(self.studies)