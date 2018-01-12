from sumstats.trait import loader
import pytest
import os
from tests.trait.test_constants import *
from sumstats.utils.dataset import Dataset
import sumstats.utils.group as gu


class TestUnitLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")
        self.name_to_dset = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        otherarray = []

        self.name_to_dset['other'] = otherarray

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)

    def test_open_with_None_array(self):
        otherarray = None

        self.name_to_dset['other'] = otherarray

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)

    def test_create_trait_group(self):
        load = loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)
        group = load._create_trait_group()
        assert group is not None
        assert group.name == "/Trait1"

    def test_create_trait_group_twice(self):
        load = loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)
        group = load._create_trait_group()
        assert group is not None
        assert group.name == "/Trait1"

        group_retrieved = load._create_trait_group()
        assert group_retrieved == group
        assert group.name == "/Trait1"

    def test_create_study_group(self):
        load = loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)

        assert study_group is not None
        assert study_group.name == "/Trait1/Study1"

    def test_create_study_group_twice_raises_error(self):
        load = loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)

        assert study_group is not None
        assert study_group.name == "/Trait1/Study1"

        with pytest.raises(ValueError):
            load._create_study_group(trait_group)

    def test_create_dataset(self):
        load = loader.Loader(None, self.h5file, "Study1", "Trait1", self.name_to_dset)
        trait_group = load._create_trait_group()
        study_group = load._create_study_group(trait_group)
        dset_name = CHR_DSET
        data = Dataset([1, 2, 3])
        gu.create_dataset(study_group, dset_name, data)

        dataset = self.f.get("/Trait1/Study1/" + CHR_DSET)

        assert dataset is not None
        assert dataset.name == "/Trait1/Study1/" + CHR_DSET
        assert len(dataset[:]) == len(data)

        data_2 = Dataset([2, 3, 4])
        with pytest.raises(RuntimeError):
            gu.create_dataset(study_group, dset_name, data_2)

        dset_name = "random"
        with pytest.raises(KeyError):
            gu.create_dataset(study_group, dset_name, data_2)
