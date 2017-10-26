import os
import pytest
import sumstats.snp.loader as loader
from tests.snp.test_constants import *
from sumstats.snp.constants import *


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        other_array = []

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array, 'freq': frequencyarray}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", dict)

    def test_open_with_None_array(self):

        other_array = None

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", dict)

    def test_create_dataset(self):
        random_group = self.f.create_group("random_group")
        data = 'string1'
        dset_name = STUDY_DSET
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        data = 1
        dset_name = BP_DSET
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        data = 0.2
        dset_name = OR_DSET
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        dset_name = "random name"
        with pytest.raises(KeyError):
            loader.create_dataset(random_group, dset_name, data)

    def test_expand_dataset(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        loader.create_dataset(random_group, dset_name, data)
        data2 = 'random string4'
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == 'string1'
        assert dataset[1] == 'random string4'

        data = 1
        dset_name = CHR_DSET
        loader.create_dataset(random_group, dset_name, data)
        data2 = 2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == data
        assert dataset[1] == data2

        data = 0.1
        dset_name = MANTISSA_DSET
        loader.create_dataset(random_group, dset_name, data)
        data2 = 0.2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == data
        assert dataset[1] == data2

    def test_expand_not_existing_dataset(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        loader.expand_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)

        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == 'string1'

        data2 = 'str2'
        loader.expand_dataset(random_group, dset_name, data2)
        dset = random_group.get(dset_name)
        dataset = dset[:]
        assert len(dataset) == 2
