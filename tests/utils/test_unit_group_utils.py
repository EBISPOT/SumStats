import os

import h5py
import numpy as np
import pytest
import sumstats.utils.group_utils as gu


class TestQueryUtils(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_get_group_from_parent(self):
        self.f.create_group("1")
        group = gu.get_group_from_parent(self.f, 1)
        assert group.name == "/1"

        group = gu.get_group_from_parent(self.f, "1")
        assert group.name == "/1"

        with pytest.raises(ValueError):
            gu.get_group_from_parent(self.f, "23")

        group.create_group("subgroup")
        subgroup = gu.get_group_from_parent(group, "subgroup")
        assert subgroup.name == "/1/subgroup"

        with pytest.raises(ValueError):
            gu.get_group_from_parent(group, "subgroup1")

        with pytest.raises(ValueError):
            gu.get_group_from_parent(self.f, "subgroup")

    def test_get_all_groups_from_parent(self):
        self.f.create_group("1")
        self.f.create_group("1/sub1")
        self.f.create_group("1/sub2")
        group1 = gu.get_group_from_parent(self.f, 1)
        groups = gu.get_all_groups_from_parent(group1)
        assert len(groups) == 2
        assert isinstance(groups[0], h5py._hl.group.Group)

    def test_get_dset(self):
        group = self.f.create_group("1")
        data = np.array([1, 2, 3])
        group.create_dataset("dset", data=data)

        dataset = gu.get_dset(group, "dset")
        assert np.array_equal(dataset, data)

        dataset = gu.get_dset(group, "dset1")
        assert dataset is None

    def test_get_dset_from_group(self):
        chr_group_2 = self.f.create_group("/2")

        with pytest.raises(LookupError):
            gu.get_dset_from_group('snp', chr_group_2)