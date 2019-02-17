import os
import pytest
import sumstats.chr.loader as loader
from tests.prep_tests import *
from sumstats.chr.constants import *
from sumstats.errors.error_classes import *
from config import properties
from sumstats.chr.study_deleter import Deleter
import shutil


class TestLoader(object):
    h5file = "./output/bychr/testfile.h5"
    f = None

    def setup_method(self, method):
        os.makedirs('./output/bychr')

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        properties.h5files_path = "./output"
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="r+")
        self.deleter1 = Deleter(study='PM001', config_properties=properties)
        self.deleter2 = Deleter(study='PM002', config_properties=properties)
        self.deleter3 = Deleter(study='PM003', config_properties=properties)

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_study_group_deleted(self):
        block11_study1 = self.f.get("/1/1200000/PM001")
        assert block11_study1 is not None
        self.deleter1.delete_study()
        block11_study1 = self.f.get("/1/1200000/PM001")
        assert block11_study1 is None
        block11 = self.f.get("/1/1200000")
        assert "PM001" not in block11
        assert "PM002" in block11



