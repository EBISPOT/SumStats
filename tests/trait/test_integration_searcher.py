import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.searcher import Search


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
        chrarray1 = [10, 10, 10, 10]
        chrarray2 = [9, 9, 9, 9]
        orarray = [0.92090, 1.01440, 0.97385, 0.99302]
        bparray = [1118275, 1120431, 49129966, 48480252]
        effectarray = ["A", "B", "C", "D"]
        otherarray = ["Z", "Y", "X", "W"]

        dict = {}
        dict["snp"] = snpsarray
        dict["pval"] = pvalsarray
        dict["chr"] = chrarray1
        dict["or"] = orarray
        dict["bp"] = bparray
        dict["effect"] = effectarray
        dict["other"] = otherarray

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", dict)
        load.load()
        load = loader.Loader(None, self.h5file, "PM002", "Trait1", dict)
        load.load()
        load = loader.Loader(None, self.h5file, "PM003", "Trait2", dict)
        load.load()

        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_1_retrieve_all_information_for_trait_1(self):
        dictionary_of_dsets = self.query.query_for_trait("Trait1")
        assert len(dictionary_of_dsets["snp"]) == 8

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 2

    def test_query_1_retrieve_all_information_for_trait_2(self):
        dictionary_of_dsets = self.query.query_for_trait("Trait2")
        assert len(dictionary_of_dsets["snp"]) == 4

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 1

    def test_query_2_retrieve_all_info_for_study_PM001(self):
        dictionary_of_dsets = self.query.query_for_study("Trait1", "PM001")

        assert len(dictionary_of_dsets["snp"]) == 4

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

    # def test_retrieve_all_info(self):
    #     dictionary_of_dsets = query.get_dsets_from_file(self.f)
    #     assert len(dictionary_of_dsets["snp"]) == 12
    #
    #     assert "PM001" in dictionary_of_dsets["study"]
    #     assert "PM003" in dictionary_of_dsets["study"]
    #     assert "PM002" in dictionary_of_dsets["study"]
    #
    #     assert 9 in chr
    #     assert 10 in chr
    #
    #     snps_set = as_string_set(dictionary_of_dsets["snp"])
    #     assert snps_set.__len__() == 4

    def test_retrieve_all_info_from_study(self):
        dictionary_of_dsets = self.query.query_for_study("Trait1", "PM001")
        assert len(dictionary_of_dsets["snp"]) == 4

    def test_non_existing_trait(self):
        with pytest.raises(ValueError):
            self.query.query_for_trait("Trait3")

    def test_non_existing_trait_study_combination(self):
        with pytest.raises(ValueError):
            self.query.query_for_study("Trait3", "PM002")


def as_string_set(list):
    my_set = set()
    for element in list:
        my_set.add(str(element))
    return my_set
