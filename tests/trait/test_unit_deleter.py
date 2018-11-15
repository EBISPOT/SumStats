import os

import pytest

import sumstats.trait.loader as loader
from sumstats.utils.interval import FloatInterval
from sumstats.trait.deleter import Deleter
from tests.prep_tests import *
import tests.test_constants as search_arrays
from config import properties
from sumstats.errors.error_classes import *
import shutil


trait1 = "t1"
trait2 = "t2"
study1 = "s1"
study2 = "s2"
study3 = "s3"

class TestUnitDeleter(object):

    output_location = './output/bytrait/'

    h5file1 = output_location + 'file_t1.h5'
    h5file2 = output_location + 'file_t2.h5'

    def setup_method(self):
        os.makedirs('./output/bytrait')
        search_arrays.chrarray = [10, 10, 10, 10]

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study1, loader=loader,
                                                        trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study2, loader=loader,
                                                        trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file2, study=study3, loader=loader,
                                                        trait=trait2,
                                                        test_arrays=search_arrays)
        load.load()

        properties.h5files_path = "./output"
        self.delete = Deleter(study=study1)

    def teardown_method(self):
        shutil.rmtree('./output')

    #def test_get_study_group(self):
    #    find_study_group = self.delete.find_study_group()[1]
    #    assert find_study_group.get_name() == "/{t}/{s}".format(t=trait1, s=study1)

    #def test_delete_study(self):
    #    assert self.delete.delete_study() == "/{t}/{s}".format(t=trait1, s=study1)