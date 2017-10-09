from sumstats.trait import loader
import numpy as np
import pytest
import os
import h5py


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

        dict = {}
        dict["snp"] = snpsarray
        dict["pval"] = pvalsarray
        dict["chr"] = chrarray
        dict["or"] = orarray
        dict["bp"] = bparray
        dict["effect"] = effect_array
        dict["other"] = other_array

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)

    def test_open_with_None_array(self):
        snpsarray = np.array(["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"])
        pvalsarray = np.array([0.4865, 0.4314, 0.5986, 0.7057])
        chrarray = np.array([1, 1, 2, 2])
        orarray = np.array([0.92090, 1.01440, 0.97385, 0.99302])
        bparray = np.array([1118275, 1120431, 49129966, 48480252])
        effect_array = np.array(["A", "B", "C", "D"])
        other_array = None

        dict = {}
        dict["snp"] = snpsarray
        dict["pval"] = pvalsarray
        dict["chr"] = chrarray
        dict["or"] = orarray
        dict["bp"] = bparray
        dict["effect"] = effect_array
        dict["other"] = other_array

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)