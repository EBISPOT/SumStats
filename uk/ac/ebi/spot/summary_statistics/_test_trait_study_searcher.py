import os

import h5py
import pytest
from uk.ac.ebi.spot.summary_statistics.trait_study_data import loader

from uk.ac.ebi.spot.summary_statistics.trait_study_data import searcher as query


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

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", snpsarray, pvalsarray, chrarray1, orarray, bparray, effectarray, otherarray)
        load.load()
        load = loader.Loader(None, self.h5file, "PM002", "Trait1", snpsarray, pvalsarray, chrarray2, orarray, bparray, effectarray, otherarray)
        load.load()
        load = loader.Loader(None, self.h5file, "PM003", "Trait2", snpsarray, pvalsarray, chrarray1, orarray, bparray, effectarray, otherarray)
        load.load()

        # open h5 file in read mode
        self.f = h5py.File(self.h5file, mode="r")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_1_retrieve_all_information_for_trait_1(self):
        dictionary_of_dsets = query.query_for_trait(self.f, "Trait1")
        assert len(dictionary_of_dsets["snp"]) == 8

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 2

    def test_query_1_retrieve_all_information_for_trait_2(self):
        dictionary_of_dsets = query.query_for_trait(self.f, "Trait2")
        assert len(dictionary_of_dsets["snp"]) == 4

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 1

    def test_query_2_retrieve_all_info_for_study_PM001(self):
        dictionary_of_dsets = query.query_for_study(self.f, "Trait1", "PM001")

        assert len(dictionary_of_dsets["snp"]) == 4

        study_set = as_string_set(dictionary_of_dsets["study"])

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

    def test_query_3_get_info_for_snp_rs185339560(self):
        dictionary_of_dsets = query.query_for_snp(self.f, "rs185339560")
        snp_set = as_string_set(dictionary_of_dsets["snp"])

        assert snp_set.__len__() == 1
        assert snp_set.pop() == "rs185339560"

        assert len(dictionary_of_dsets["study"]) == 3

        pvals = dictionary_of_dsets["pval"]
        assert pvals[0] == pvals[1] == pvals[2]

        assert "PM001" in dictionary_of_dsets["study"]
        assert "PM002" in dictionary_of_dsets["study"]
        assert "PM003" in dictionary_of_dsets["study"]

    def test_query_4_get_info_for_chromosome_10(self):
        dictionary_of_dsets = query.query_for_chromosome(self.f, 10)
        assert len(dictionary_of_dsets["snp"]) == 8

        chr = dictionary_of_dsets["chr"]
        assert len(chr) == 8
        assert chr[0] == 10
        assert chr[1] == 10
        assert chr[2] == 10
        assert chr[3] == 10
        assert chr[4] == 10
        assert chr[5] == 10
        assert chr[6] == 10
        assert chr[7] == 10

        assert "PM002" not in dictionary_of_dsets["study"]
        assert "PM001" in dictionary_of_dsets["study"]
        assert "PM003" in dictionary_of_dsets["study"]

    def test_query_4_get_info_for_chromosome_9(self):
        dictionary_of_dsets = query.query_for_chromosome(self.f, 9)
        assert len(dictionary_of_dsets["snp"]) == 4

        chr = dictionary_of_dsets["chr"]
        assert len(chr) == 4
        assert chr[0] == 9
        assert chr[1] == 9
        assert chr[2] == 9
        assert chr[3] == 9

        assert "PM001" not in dictionary_of_dsets["study"]
        assert "PM002" in dictionary_of_dsets["study"]
        assert "PM003" not in dictionary_of_dsets["study"]

    def test_query_5_get_all_info_for_snp_rs185339560_and_Trait1(self):
        dictionary_of_dsets = query.query_for_snp(self.f, "rs185339560", "Trait1")
        # Study - Trait
        # PM001 - Trait1
        # PM002 - Trait1
        # PM003 - Trait2
        assert "PM003" not in dictionary_of_dsets["study"]
        assert "PM001" in dictionary_of_dsets["study"]
        assert "PM002" in dictionary_of_dsets["study"]

        snp_set = as_string_set(dictionary_of_dsets["snp"])

        assert snp_set.__len__() == 1
        assert snp_set.pop() == "rs185339560"

    # Study - Trait - Chromosome
    # PM001 - Trait1 - 10
    # PM002 - Trait1 - 9
    # PM003 - Trait2 - 10

    def test_query_6_all_info_for_chromosome_9_and_trait(self):
        dictionary_of_dsets = query.query_for_chromosome(self.f, "9", "Trait1")
        study = dictionary_of_dsets["study"]
        assert "PM002" in study
        assert "PM001" not in study
        assert "PM003" not in study

        assert len(dictionary_of_dsets["snp"]) == 4

        dictionary_of_dsets = query.query_for_chromosome(self.f, "9", "Trait2")
        assert len(dictionary_of_dsets["snp"]) == 0

    def test_query_6_all_info_for_chromosome_10_and_trait(self):
        dictionary_of_dsets = query.query_for_chromosome(self.f, "10", "Trait1")
        study = dictionary_of_dsets["study"]
        assert "PM001" in study
        assert "PM003" not in study
        assert "PM002" not in study

        assert len(dictionary_of_dsets["snp"]) == 4

        dictionary_of_dsets = query.query_for_chromosome(self.f, "10", "Trait2")
        study = dictionary_of_dsets["study"]
        assert "PM003" in study
        assert "PM001" not in study
        assert "PM002" not in study

        assert len(dictionary_of_dsets["snp"]) == 4

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
        dictionary_of_dsets = query.query_for_study(self.f, "Trait1", "PM001")
        assert len(dictionary_of_dsets["snp"]) == 4

    def test_non_existing_trait(self):
        with pytest.raises(ValueError):
            query.query_for_trait(self.f, "Trait3")

    def test_non_existing_trait_study_combination(self):
        with pytest.raises(ValueError):
            query.query_for_study(self.f, "Trait3", "PM002")


def as_string_set(list):
    my_set = set()
    for element in list:
        my_set.add(str(element))
    return my_set