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

    def test_find_h5file_study_group(self):
        find_study_group = self.deleter1._find_h5file_study_group()
        assert find_study_group is not None
        assert len(find_study_group) == 1
        assert len(find_study_group.keys()) == 1
        for key, value_list in find_study_group.items():
            assert key == "./output/bychr/testfile.h5"
            for value in value_list:
                assert "PM001" in value
                assert "PM002" not in value
        with pytest.raises(NotFoundError):
            self.deleter = Deleter(study='PM004', config_properties=properties)
            self.deleter._find_h5file_study_group()