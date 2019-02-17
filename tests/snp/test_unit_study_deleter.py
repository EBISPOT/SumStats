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
    h5file = "./output/bysnp/testfile.h5"
    f = None

    def setup_method(self, method):
        os.makedirs('./output/bysnp')

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        properties.h5files_path = "./output"
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        shutil.rmtree('./output')

    def test_find_h5file_study_group(self):
        self.deleter = Deleter(study='PM001', config_properties=properties)
        find_study_group = self.deleter._find_h5file_study_group()
        assert len(find_study_group) == 1
        assert len(find_study_group.keys()) == 1
        for key, value_list in find_study_group.items():
            assert key == "./output/bysnp/testfile.h5"
            for value in value_list:
                assert "PM001" in value
                assert "PM002" not in value
        with pytest.raises(NotFoundError):
            self.deleter = Deleter(study='PM004', config_properties=properties)
            self.deleter._find_h5file_study_group()
