import os

import h5py
import numpy as np
import pytest

from SumStats.uk_ac_ebi_spot.summary_statistics.chr_block_snp_data import loader


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        snpsarray = np.array(["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"])
        pvalsarray = np.array([0.4865, 0.4314, 0.5986, 0.7057])
        chrarray = np.array([1, 1, 2, 2])
        orarray = np.array([0.92090, 1.01440, 0.97385, 0.99302])
        bparray = np.array([1118275, 1120431, 49129966, 48480252])
        effect_array = np.array(["A", "B", "C", "D"])
        other_array = np.array([])
        with pytest.raises(SystemExit):
            loader.Loader(None, self.h5file, "PM001", snpsarray, pvalsarray, chrarray, orarray, bparray, effect_array,
                          other_array)

    def test_open_with_None_array(self):
        snpsarray = np.array(["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"])
        pvalsarray = np.array([0.4865, 0.4314, 0.5986, 0.7057])
        chrarray = np.array([1, 1, 2, 2])
        orarray = np.array([0.92090, 1.01440, 0.97385, 0.99302])
        bparray = np.array([1118275, 1120431, 49129966, 48480252])
        effect_array = np.array(["A", "B", "C", "D"])
        other_array = None
        with pytest.raises(SystemExit):
            loader.Loader(None, self.h5file, "PM001", snpsarray, pvalsarray, chrarray, orarray, bparray, effect_array,
                          other_array)

    def test_create_dataset(self):
        random_group = self.f.create_group("random_group")
        data = "random string"
        dset_name = "random dset"
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        data = dset[:]
        assert len(data) == 1
        assert data[0] == "random string"

        data = 1
        dset_name = "random_dset"
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        data = dset[:]
        assert len(data) == 1
        assert data[0] == 1

        data = 0.2
        dset_name = "random_dset_"
        loader.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        data = dset[:]
        assert len(data) == 1
        assert data[0] == 0.2

    def test_expand_dataset(self):
        random_group = self.f.create_group("random group")

        data = "random string"
        dset_name = "random dset"
        loader.create_dataset(random_group, dset_name, data)
        data2 = "random string 2"
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dset_data = dset[:]
        assert dset_data[0] == data
        assert dset_data[1] == data2

        data = 1
        dset_name = "random_dset"
        loader.create_dataset(random_group, dset_name, data)
        data2 = 2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dset_data = dset[:]
        assert dset_data[0] == 1
        assert dset_data[1] == 2

        data = 0.1
        dset_name = "random_dset_"
        loader.create_dataset(random_group, dset_name, data)
        data2 = 0.2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dset_data = dset[:]
        assert dset_data[0] == 0.1
        assert dset_data[1] == 0.2

    def test_expand_not_existing_dataset(self):
        random_group = self.f.create_group("random group")

        data = "random string"
        dset_name = "random dset"
        loader.expand_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)

        assert dset is not None
        dset_data = dset[:]
        assert len(dset_data) == 1
        assert dset_data[0] == data

        data2 = "random string 2"
        loader.expand_dataset(random_group, dset_name, data2)
        dset = random_group.get(dset_name)
        dset_data = dset[:]
        assert len(dset_data) == 2


    def test_create_chromosome_groups(self):
        array_of_chromosomes = ["1", 2, "X"]
        loader.create_chromosome_groups(self.f, array_of_chromosomes)
        chr1 = self.f.get("1")
        assert chr1 is not None
        chr2 = self.f.get("2")
        assert chr2 is not None
        chrX = self.f.get("X")
        assert chrX is not None

