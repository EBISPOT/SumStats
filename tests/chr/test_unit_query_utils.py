import os
import h5py
import pytest
import numpy as np
import sumstats.chr.loader as loader
import sumstats.chr.query_utils as query


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
        chrarray = [1, 1, 2, 2]
        orarray = [0.92090, 1.01440, 0.97385, 0.99302]
        bparray = [1118275, 1120431, 49129966, 48480252]
        effect_array = ["A", "B", "C", "D"]
        other_array = ["Z", "Y", "X", "W"]

        dict = {}
        dict["snp"] = snpsarray
        dict["pval"] = pvalsarray
        dict["chr"] = chrarray
        dict["or"] = orarray
        dict["bp"] = bparray
        dict["effect"] = effect_array
        dict["other"] = other_array

        load = loader.Loader(None, self.h5file, 'PM001', dict)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM002', dict)
        load.load()
        load = loader.Loader(None, self.h5file, 'PM003', dict)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_block_groups_from_parent_within_block_range(self):
        chr_group_1 = self.f.get("1")
        chr_group_2 = self.f.get("2")

        with pytest.raises(ValueError):
            query.get_block_groups_from_parent_within_block_range(chr_group_1, 1118275, 1118276)

        with pytest.raises(TypeError):
            query.get_block_groups_from_parent_within_block_range(chr_group_1, None, 1200000)

        with pytest.raises(AttributeError):
            query.get_block_groups_from_parent_within_block_range(None, 1200000, 1200000)

        blocks = query.get_block_groups_from_parent_within_block_range(chr_group_1, 1200000, 1200000)
        assert blocks.__class__ is list
        assert len(blocks) == 1
        assert blocks[0].__class__ == h5py._hl.group.Group

        blocks = query.get_block_groups_from_parent_within_block_range(chr_group_2, 48500000, 49200000)
        assert len(blocks) == 8
        assert blocks[0].name == "/2/48500000"
        assert blocks[7].name == "/2/49200000"

        with pytest.raises(ValueError):
            query.get_block_groups_from_parent_within_block_range(chr_group_2, 49200000, 48500000)

    def test_get_dict_of_wanted_dsets_from_groups(self):
        chr_group_2 = self.f.get("/2")
        TO_QUERY_DSETS = ['snp', 'pval', 'or', 'study', 'bp', 'effect', 'other']

        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, 48500000, 49200000)

        dict_of_dsets = query.get_dict_of_wanted_dsets_from_groups(TO_QUERY_DSETS, block_groups)
        assert dict_of_dsets.__class__ is dict

        for dset_name in TO_QUERY_DSETS:
            # 2 values for each of 3 studies that we loaded
            assert len(dict_of_dsets[dset_name]) == 6
            assert dict_of_dsets[dset_name].__class__ is np.ndarray

        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, 48600000, 48600000)
        dict_of_dsets = query.get_dict_of_wanted_dsets_from_groups(TO_QUERY_DSETS, block_groups)
        for dset_name in TO_QUERY_DSETS:
            # no SNP bp falls into this group
            assert len(dict_of_dsets[dset_name]) == 0

    def test_get_dset_from_group(self):
        chr_group_2 = self.f.get("/2")

        block_groups = query.get_block_groups_from_parent_within_block_range(chr_group_2, 48500000, 48500000)
        block_group = block_groups[0]
        snp_group = block_group.get("rs7085086")

        TO_QUERY_DSETS = ['snp', 'pval', 'study', 'or', 'bp', 'effect', 'other']
        for dset_name in TO_QUERY_DSETS:
            dset = query.get_dset_from_group(dset_name, snp_group)
            if dset_name is "snp":
                assert len(dset) == 0
            else:
                assert len(dset) == 3
                if dset_name is "study":
                    assert len(set(dset)) == 3
                else:
                    assert len(set(dset)) == 1

    def test_get_block_number(self):
        print()
        bp = 0
        block_size = 100000
        assert query.get_block_number(bp) == block_size

        bp = 50000
        assert query.get_block_number(bp) == block_size

        bp = 100000
        assert query.get_block_number(bp) == block_size

        bp = 100001
        assert query.get_block_number(bp) == 2*block_size

        bp = 110000
        assert query.get_block_number(bp) == 2*block_size

        bp = 200000
        assert query.get_block_number(bp) == bp

        bp = 900000
        assert query.get_block_number(bp) == bp

        bp = 900001
        assert query.get_block_number(bp) == 1000000

        bp = 999999
        assert query.get_block_number(bp) == 1000000

        bp = 1100000
        assert query.get_block_number(bp) == bp

        bp = 1100001
        assert query.get_block_number(bp) == 1200000
