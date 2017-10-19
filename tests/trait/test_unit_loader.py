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
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = ["0.4865", "0.4314", "0.5986", "0.7057"]
        chrarray = ["1", "1", "2", "2"]
        orarray = ["0.92090", "1.01440", "0.97385", "0.99302"]
        bparray = ["1118275", "1120431", "49129966", "48480252"]
        effect_array = ["A", "B", "C", "D"]
        other_array = []
        frequencyarray = ["3.926e-01", "4.900e-03", "1.912e-01", "7.000e-04"]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effect_array, "other": other_array, 'freq': frequencyarray}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)

    def test_open_with_None_array(self):
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = ["0.4865", "0.4314", "0.5986", "0.7057"]
        chrarray = ["1", "1", "2", "2"]
        orarray = ["0.92090", "1.01440", "0.97385", "0.99302"]
        bparray = ["1118275", "1120431", "49129966", "48480252"]
        effect_array = ["A", "B", "C", "D"]
        other_array = None
        frequencyarray = ["3.926e-01", "4.900e-03", "1.912e-01", "7.000e-04"]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effect_array, "other": other_array, 'freq': frequencyarray}

        with pytest.raises(ValueError):
            loader.Loader(None, self.h5file, "PM001", "Trait1", dict)