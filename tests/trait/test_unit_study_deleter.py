import os

import pytest

import sumstats.trait.loader as loader
from tests.prep_tests import *
from sumstats.trait.constants import *
from sumstats.trait.study_deleter import Deleter
from sumstats.errors.error_classes import *
from config import properties
import shutil


class TestDeleter(object):
    h5file1 = "./output/bytrait/file_t1.h5"
    h5file2 = "./output/bytrait/file_t2.h5"
    f = None

    def setup_method(self, method):
        os.makedirs('./output/bytrait')

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study='PM001', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study='PM002', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file2, study='PM003', trait='Trait2', loader=loader)
        load.load()

        properties.h5files_path = "./output"

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_find_h5file_study_group(self):
        self.deleter = Deleter(study='PM001', config_properties=properties)
        find_study_group = self.deleter._find_h5file_study_group()
        assert len(find_study_group) == 1
        assert len(find_study_group.keys()) == 1
        for key, value in find_study_group.items():
            assert key == "./output/bytrait/file_t1.h5"
            assert value == "/Trait1/PM001"
        with pytest.raises(NotFoundError):
            self.deleter = Deleter(study='PM004', config_properties=properties)
            self.deleter._find_h5file_study_group()

    def test_delete_trait_if_no_children(self):
        self.deleter = Deleter(study='PM001', config_properties=properties)
        assert self.deleter._trait_has_no_children_left('Trait1') == False
        self.deleter = Deleter(study='PM003', config_properties=properties)
        assert self.deleter._trait_has_no_children_left('Trait2') == True

    def test_delete_study(self):
        with pytest.raises(NotFoundError):
            self.deleter = Deleter(study='PM004', config_properties=properties)
            self.deleter.delete_study()


