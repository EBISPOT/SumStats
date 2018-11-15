import os

import sumstats.trait.loader as loader
from tests.prep_tests import *
from sumstats.trait.constants import *
from sumstats.trait.deleter import Deleter
from config import properties
import shutil


class TestDeleter(object):
    h5file = "./output/bytrait/testfile.h5"
    f = None

    def setup_method(self, method):
        os.makedirs('./output/bytrait')

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM001', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM002', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM003', trait='Trait2', loader=loader)
        load.load()

        properties.h5files_path = "./output"
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="r+")
        self.deleter = Deleter(study='PM001', config_properties=properties)

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_study_deleted(self):
        trait_1 = self.f.get("Trait1")

        self.deleter.delete_study()
        #assert x == '/Trait1/PM001'
        assert len(trait_1.keys()) == 1
