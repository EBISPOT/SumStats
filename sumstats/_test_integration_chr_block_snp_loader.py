import os

import h5py
import numpy as np

from sumstats.chr_block_snp_data import loader


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        dt=h5py.special_dtype(vlen=str)
        snpsarray = np.array(["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"], dtype=dt)
        pvalsarray = np.array([0.4865, 0.4314, 0.5986, 0.7057])
        chrarray = np.array([1, 1, 2, 2])
        orarray = np.array([0.92090, 1.01440, 0.97385, 0.99302])
        bparray = np.array([1118275, 1120431, 49129966, 48480252])
        effect_array = np.array(["A", "B", "C", "D"])
        other_array = np.array(["Z", "Y", "X", "W"])

        load = loader.Loader(None, self.h5file, 'PM001', snpsarray, pvalsarray, chrarray, orarray, bparray,
                             effect_array, other_array)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM002', snpsarray, pvalsarray, chrarray, orarray, bparray,
                             effect_array, other_array)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM003', snpsarray, pvalsarray, chrarray, orarray, bparray,
                             effect_array, other_array)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_chromosome_groups(self):
        chr_group_1 = self.f.get("1")
        assert chr_group_1 is not None

        chr_group_2 = self.f.get("2")
        assert chr_group_2 is not None

    def test_block_groups(self):
        chr_group_1 = self.f.get("1")

        block1 = chr_group_1.get("1200000")
        assert block1 is not None
        assert block1.name == "/1/1200000"
        assert len(chr_group_1.keys()) == 1

        chr_group_2 = self.f.get("2")

        blocks = list(chr_group_2.keys())
        assert len(blocks) == 2


        assert blocks[0] == "48500000"
        assert blocks[1] == "49200000"

    def test_snps_in_blocks(self):
        block11 = self.f.get("/1/1200000")
        snps = block11.keys()
        assert len(snps) == 2
        assert block11.get("rs185339560") is not None
        assert block11.get("rs11250701") is not None

        block21 = self.f.get("/2/48500000")
        snps = block21.keys()
        assert len(snps) == 1
        assert block21.get("rs7085086") is not None

        block22 = self.f.get("/2/49200000")
        snps = block22.keys()
        assert len(snps) == 1
        assert block22.get("chr10_2622752_D") is not None

    def test_snp_group_content(self):
        snp1 = self.f.get("/1/1200000/rs185339560")
        assert snp1 is not None
        info = snp1.keys()
        assert len(info) == 6

        pvals = snp1.get("pval")
        assert len(pvals[:]) == 3  # loaded 3 times for 3 diff studies
        assert pvals[:][0] == 0.4865

        studies = snp1.get("study")
        assert len(studies[:]) == 3
        assert studies[:][0] == "PM001"
        assert studies[:][1] == "PM002"
        assert studies[:][2] == "PM003"
