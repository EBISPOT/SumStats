import os
import pytest
import sumstats.snp.loader as loader
from tests.prep_tests import *
from sumstats.snp.constants import *
from sumstats.errors.error_classes import *
from config import properties
from sumstats.snp.study_deleter import Deleter
import shutil


class TestLoader(object):
    h5file = "./output/bysnp/1/testfile.h5"
    h5file2 = "./output/bysnp/2/testfile.h5"
    f = None
    f2 = None

    def setup_method(self, method):
        os.makedirs('./output/bysnp/1/')
        os.makedirs('./output/bysnp/2/')

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file2, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file2, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file2, 'PM003', loader)
        load.load()


        properties.h5files_path = "./output"
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="r+")
        self.f2 = h5py.File(self.h5file2, mode="r+")
        self.deleter1 = Deleter(study='PM001', config_properties=properties)
        self.deleter2 = Deleter(study='PM002', config_properties=properties)
        self.deleter3 = Deleter(study='PM003', config_properties=properties)

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_study_group_deleted(self):
        snp1 = self.f.get("/rs185339560")
        snp1_2 = self.f2.get("/rs185339560")
        assert snp1 is not None
        info = list(snp1["PM001"].keys())
        assert len(info) == len(TO_STORE_DSETS)
        assert len(snp1) == 3
        self.deleter1.delete_study()
        assert "PM002" in snp1
        assert "PM001" not in snp1
        assert len(snp1) == 2

        assert "PM002" in snp1_2
        assert "PM001" not in snp1_2
        assert len(snp1_2) == 2

    def test_snp_groups_deleted_when_no_studies_belong_to_it(self):
        self.deleter1.delete_study()
        self.deleter2.delete_study()
        self.deleter3.delete_study()
        snp1 = self.f.get("/rs185339560")
        assert snp1 is None
