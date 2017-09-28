import h5py
import os
import h5py_a as loader
import h5py_a_cleanup as cleanup
import h5py_a_query as query
import pytest


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None
    snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
    pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
    chrarray1 = [10, 10, 10, 10]
    orarray = [0.92090, 1.01440, 0.97385, 0.99302]

    def setup_method(self, method):

        load = loader.Loader(None, ".testfile.h5", "PM001", self.snpsarray, self.pvalsarray, self.chrarray1, self.orarray, 10, 11)
        load.load()
        load = loader.Loader(None, ".testfile.h5", "PM002", self.snpsarray, self.pvalsarray, self.chrarray1, self.orarray, 10, 11)
        load.load()
        load = loader.Loader(None, ".testfile.h5", "PM003", self.snpsarray, self.pvalsarray, self.chrarray1, self.orarray, 10, 11)
        load.load()

        # open h5 file in read mode
        self.f = h5py.File(".testfile.h5", mode="a")

        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM001")
        assert len(info_array) != 0
        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM002")
        assert len(info_array) != 0
        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM001")
        assert len(info_array) != 0

    def test_remove_PM001(self):
        cleanup.remove_study_elements(self.f, "PM001", self.snpsarray, self.pvalsarray, self.chrarray1, self.orarray)
        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM001")

        assert len(info_array) == 0

        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM002")
        assert len(info_array) != 0

        info_array = query.get_all(self.f)
        info_array = query.filter_by_study(info_array, "PM003")
        assert len(info_array) != 0

    def teardown_method(self, method):
        os.remove(".testfile.h5")


def as_string_set(list):
    my_set = set()
    for element in list:
        my_set.add(str(element))
    return my_set
