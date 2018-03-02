import os

import pytest

from sumstats.trait import loader
from sumstats.utils.dataset import Dataset
from sumstats.errors.error_classes import *
from tests.prep_tests import *


class TestUnitLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        other_array = []
        loader_dictionary = prepare_dictionary()
        loader_dictionary['other'] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "Study1", "Trait1", loader_dictionary)

    def test_open_with_None_array(self):
        other_array = None

        loader_dictionary = prepare_dictionary()
        loader_dictionary['other'] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "Study1", "Trait1", loader_dictionary)

    def test_create_trait_group(self):
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study="Study1", trait="Trait1", loader=loader)
        group = load._create_trait_group()
        assert group is not None
        assert group.get_name() == "/Trait1"

    def test_create_trait_group_twice(self):
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study="Study1", trait="Trait1", loader=loader)
        group = load._create_trait_group()
        assert group is not None
        assert group.get_name() == "/Trait1"

        group_retrieved = load._create_trait_group()
        assert group_retrieved.get_name() == "/Trait1"

    def test_create_study_group(self):
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study="Study1", trait="Trait1", loader=loader)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)

        assert study_group is not None
        assert study_group.get_name() == "/Trait1/Study1"

    def test_create_study_group_twice_raises_error(self):
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study="Study1", trait="Trait1", loader=loader)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)

        assert study_group is not None
        assert study_group.get_name() == "/Trait1/Study1"

        with pytest.raises(AlreadyLoadedError):
            load._create_study_group(trait_group)

    def test_create_dataset(self):
        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study="Study1", trait="Trait1", loader=loader)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)
        dset_name = CHR_DSET
        data = Dataset([1, 2, 3])
        study_group.generate_dataset(dset_name, data)

        dataset = self.f.get("/Trait1/Study1/" + CHR_DSET)

        assert dataset is not None
        assert dataset.name == "/Trait1/Study1/" + CHR_DSET
        assert len(dataset[:]) == len(data)

        data_2 = Dataset([2, 3, 4])
        with pytest.raises(RuntimeError):
            study_group.generate_dataset(dset_name, data_2)

        dset_name = "random"
        with pytest.raises(KeyError):
            study_group.generate_dataset(dset_name, data_2)
