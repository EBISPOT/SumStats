import h5py
import os
import h5py_a as loader
import pytest
import numpy as np


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

    def test_get_chr_mask(self):
        chromosome_array = np.asarray([1, 2, 3, 1])
        mask = loader.get_chr_mask("1", chromosome_array)
        expected_mask = [True, False, False, True]
        assert np.array_equal(expected_mask, mask)
        mask = loader.get_chr_mask(1, chromosome_array)
        assert np.array_equal(expected_mask, mask)

    def test_filter_from_mask(self):
        vector = np.asarray([1, 2, 3, 4])
        mask = [True, False, False, True]
        masked_vector = loader.filter_from_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == 1
        assert masked_vector[1] == 4

        vector = np.asarray(["a", "b", "c", "d"])
        masked_vector = loader.filter_from_mask(vector, mask)
        assert len(masked_vector) == 2
        assert masked_vector[0] == "a"
        assert masked_vector[1] == "d"

    def test_get_chr_group(self):
        self.f.create_group("1")
        group = loader.get_chr_group(self.f, 1)
        assert group.name == "/1"

        group = loader.get_chr_group(self.f, "1")
        assert group.name == "/1"

        with pytest.raises(SystemExit):
            loader.get_chr_group(self.f, "23")

    def test_get_block_mask(self):
        block_floor = 0
        block_ceil = block_size = 100000
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000])
        expected_mask = [True, True, False, True, True, False]
        block_mask = loader.get_block_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

        block_floor = block_ceil + 1
        block_ceil += block_size
        bp_chr_array = np.asarray([0, 100000, 100001, 1, 50000, 200000, 200001, 300000])
        expected_mask = [False, False, True, False, False, True, False, False]
        block_mask = loader.get_block_mask(block_floor, block_ceil, bp_chr_array)
        assert np.array_equal(expected_mask, block_mask)

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
        print dset_data
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
        print dset_data
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
        print dset_data
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

