import os
import shutil
from sumstats.errors.error_classes import *
import sumstats.explorer as ex
import sumstats.trait.loader as loader
from tests.prep_tests import *
import pytest


@pytest.yield_fixture(scope="class", autouse=True)
def load_studies(request):
    os.makedirs('./outputexplorer/bytrait')
    output_location = './outputexplorer/bytrait/'

    h5file = output_location + 'file_t1.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s1', trait='t1', loader=loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s2', trait='t1', loader=loader)
    load.load()

    h5file = output_location + 'file_t2.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s3', trait='t2', loader=loader)
    load.load()

    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s4', trait='t2', loader=loader)
    load.load()

    h5file = output_location + 'file_t3.h5'
    load = prepare_load_object_with_study_and_trait(h5file=h5file, study='s5', trait='t3', loader=loader)
    load.load()

    request.addfinalizer(remove_dir)


def remove_dir():
    shutil.rmtree('./outputexplorer')


class TestLoader(object):
    def setup_method(self):
        # initialize explorer with local path
        self.explorer = ex.Explorer("./outputexplorer")
        self.loaded_traits = ['t1', 't2', 't3']
        self.loaded_studies = ['t1:s1', 't1:s2', 't2:s3', 't2:s4', 't3:s5']
        self.loaded_studies_t1 = ['s1', 's2']
        self.loaded_studies_t3 = ['s5']

    def test_get_list_of_traits(self):
        list_of_traits = self.explorer.get_list_of_traits()
        assert len(list_of_traits) == len(self.loaded_traits)
        for trait in self.loaded_traits:
            assert trait in list_of_traits

    def test_get_list_of_studies_for_trait_t1(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t1')
        assert len(list_of_studies) == len(self.loaded_studies_t1)
        for study in self.loaded_studies_t1:
            assert study in list_of_studies

    def test_get_list_of_studies_for_trait_t3(self):
        list_of_studies = self.explorer.get_list_of_studies_for_trait('t3')
        assert len(list_of_studies) == len(self.loaded_studies_t3)
        for study in self.loaded_studies_t3:
            assert study in list_of_studies

    def test_get_list_of_studies_for_non_existing_trait_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_list_of_studies_for_trait('t4')

    def test_get_list_of_studies(self):
        list_of_studies = self.explorer.get_list_of_studies()
        assert len(list_of_studies) == len(self.loaded_studies)
        for study in self.loaded_studies:
            assert study in list_of_studies

    def test_get_info_from_study_s1(self):
        trait = self.explorer.get_trait_of_study('s1')
        assert trait == 't1'

    def test_get_info_from_non_exising_study_raises_error(self):
        with pytest.raises(NotFoundError):
            self.explorer.get_trait_of_study('s6')
