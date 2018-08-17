from sumstats.server.app import app

import os

import pytest

import sumstats.trait.loader as loader
from sumstats.utils.interval import FloatInterval
from sumstats.trait.search.study_search import StudySearch
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


class TestAPI(object):
    output_location = './output/bytrait/'

    h5file1 = output_location + 'file_t1.h5'
    h5file2 = output_location + 'file_t2.h5'

    def setup_method(self):
        os.makedirs('./output/bytrait')
        search_arrays.chrarray = [10, 10, 10, 10]

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study1, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study=study2, loader=loader, trait=trait1,
                                                        test_arrays=search_arrays)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file2, study=study3, loader=loader, trait=trait2,
                                                        test_arrays=search_arrays)
        load.load()

        self.start = 0
        self.size = 20

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_something(self):
        test_app = app.test_client()
        test_app.testing = True

        result = test_app.get("/gwas/summary-statistics/api")
        assert result.status_code == 200

    def test_something_else(self):
        properties.h5files_path = "./output"
        test_app = app.test_client()
        test_app.testing = True

        result = test_app.get("/gwas/summary-statistics/api/associations")
        json_result = result.get_json()
        assert result.status_code == 200
