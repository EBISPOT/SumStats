from sumstats.trait import loader
import pytest
import os
from tests.trait.test_constants import *
from sumstats.utils.dataset import Dataset
from sumstats.trait.constants import *


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        otherarray = []

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)

    def test_open_with_None_array(self):
        otherarray = None

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)

    def test_create_trait_group(self):
        group = loader.create_trait_group(self.f, "Trait1")
        assert group is not None
        assert group.name == "/Trait1"

        group_retrieved = loader.create_trait_group(self.f, "Trait1")
        assert group_retrieved == group
        assert group.name == "/Trait1"

        group_2 = loader.create_trait_group(self.f, "Trait2")
        assert group_2 is not None
        assert group_2.name == "/Trait2"

    def test_create_study_group(self):
        trait_group = loader.create_trait_group(self.f, "Trait1")
        study_group = loader.create_study_group(trait_group, "Study1")

        assert study_group is not None
        assert study_group.name == "/Trait1/Study1"

        with pytest.raises(ValueError):
            loader.create_study_group(trait_group, "Study1")

        study_group_2 = loader.create_study_group(trait_group, "Study2")
        assert study_group_2 is not None
        assert study_group_2.name == "/Trait1/Study2"

    def test_create_dataset(self):
        trait_group = loader.create_trait_group(self.f, "Trait1")
        study_group = loader.create_study_group(trait_group, "Study1")
        dset_name = CHR_DSET
        data = Dataset([1, 2, 3])
        loader.create_dataset(study_group, dset_name, data)

        dataset = self.f.get("/Trait1/Study1/" + CHR_DSET)

        assert dataset is not None
        assert dataset.name == "/Trait1/Study1/" + CHR_DSET
        assert len(dataset[:]) == len(data)

        data_2 = Dataset([2, 3, 4])
        with pytest.raises(ValueError):
            loader.create_dataset(study_group, dset_name, data_2)

        dset_name = "random"
        with pytest.raises(KeyError):
            loader.create_dataset(study_group, dset_name, data_2)
