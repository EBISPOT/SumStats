import h5py
import os
import h5py_1 as loader
import h5py_1_query as query
import pytest


class TestFirstApproach(object):

    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
        chrarray1 = [10, 10, 10, 10]
        chrarray2 = [9, 9, 9, 9]
        orarray = [0.92090, 1.01440, 0.97385, 0.99302]

        load = loader.Loader(None, ".testfile.h5", "PM001", "Trait1", snpsarray, pvalsarray, chrarray1, orarray)
        load.load()
        load = loader.Loader(None, ".testfile.h5", "PM002", "Trait1", snpsarray, pvalsarray, chrarray2, orarray)
        load.load()
        load = loader.Loader(None, ".testfile.h5", "PM003", "Trait2", snpsarray, pvalsarray, chrarray1, orarray)
        load.load()

        # open h5 file in read mode
        self.f = h5py.File(".testfile.h5", mode="r")

    def test_query_1_retrieve_all_information_for_trait_1(self):
        snps, pvals, chr, orvals, belongs_to = query.all_trait_info(self.f, "Trait1")
        assert len(snps) == 8

        studies = belongs_to
        study_set = as_string_set(studies)

        assert study_set.__len__() == 2

    def test_query_1_retrieve_all_information_for_trait_2(self):

        snps, pvals, chr, orvals, belongs_to = query.all_trait_info(self.f, "Trait2")
        assert len(snps) == 4

        studies = belongs_to
        study_set = as_string_set(studies)

        assert study_set.__len__() == 1

    def test_query_2_retrieve_all_info_for_study_PM001(self):

        snps, pvals, chr, orvals, belongs_to = query.all_study_info(self.f, "Trait1", "PM001")

        assert len(snps) == 4

        studies = belongs_to
        study_set = as_string_set(studies)

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

    def test_query_3_get_info_for_snp_rs185339560(self):

        snps, pvals, chr, orvals, belongs_to = query.all_snp_info(self.f, "rs185339560")
        snp_set = as_string_set(snps)

        assert snp_set.__len__() == 1
        assert snp_set.pop() == "rs185339560"

        assert len(belongs_to) == 3

        assert pvals[0] == pvals[1] == pvals[2]

        studies = belongs_to
        assert "PM001" in studies
        assert "PM002" in studies
        assert "PM003" in studies

    def test_query_4_get_info_for_chromosome_10(self):

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, 10)
        assert len(snps) == 8

        assert len(chr) == 8
        assert chr[0] == 10
        assert chr[1] == 10
        assert chr[2] == 10
        assert chr[3] == 10
        assert chr[4] == 10
        assert chr[5] == 10
        assert chr[6] == 10
        assert chr[7] == 10

        studies = belongs_to
        assert "PM002" not in studies
        assert "PM001" in studies
        assert "PM003" in studies

    def test_query_4_get_info_for_chromosome_9(self):

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, 9)
        assert len(snps) == 4

        assert len(chr) == 4
        assert chr[0] == 9
        assert chr[1] == 9
        assert chr[2] == 9
        assert chr[3] == 9

        studies = belongs_to
        assert "PM001" not in studies
        assert "PM002" in studies
        assert "PM003" not in studies

    def test_query_5_get_all_info_for_snp_rs185339560_and_Trait1(self):

        snps, pvals, chr, orvals, belongs_to = query.all_snp_info(self.f, "rs185339560", "Trait1")
        studies = belongs_to
        # Study - Trait
        # PM001 - Trait1
        # PM002 - Trait1
        # PM003 - Trait2
        assert "PM003" not in studies
        assert "PM001" in studies
        assert "PM002" in studies

        snp_set = as_string_set(snps)

        assert snp_set.__len__() == 1
        assert snp_set.pop() == "rs185339560"

    # Study - Trait - Chromosome
    # PM001 - Trait1 - 10
    # PM002 - Trait1 - 9
    # PM003 - Trait2 - 10

    def test_query_6_all_info_for_chromosome_9_and_trait(self):

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, "9", "Trait1")
        study = belongs_to
        assert "PM002" in study
        assert "PM001" not in study
        assert "PM003" not in study

        assert len(snps) == 4

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, "9", "Trait2")
        assert len(snps) == 0

    def test_query_6_all_info_for_chromosome_10_and_trait(self):

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, "10", "Trait1")
        study = belongs_to
        assert "PM001" in study
        assert "PM003" not in study
        assert "PM002" not in study

        assert len(snps) == 4

        snps, pvals, chr, orvals, belongs_to = query.all_chromosome_info(self.f, "10", "Trait2")
        study = belongs_to
        assert "PM003" in study
        assert "PM001" not in study
        assert "PM002" not in study

        assert len(snps) == 4

    def test_retrieve_all_info(self):
        snps, pvals, chr, orvals, belongs_to = query.retrieve_all_info(self.f)
        assert len(snps) == 12

        studies = belongs_to
        assert "PM001" in studies
        assert "PM003" in studies
        assert "PM002" in studies

        assert 9 in chr
        assert 10 in chr

        snps_set = as_string_set(snps)
        assert snps_set.__len__() == 4

    def test_retrieve_all_info_from_study(self):
        study_group = self.f.get("/Trait1/PM001")
        snps, pvals, chr, orvals, belongs_to =  query.retrieve_all_info_from_study("PM001", study_group)
        assert len(snps) == 4

    def test_non_existing_trait(self):
        with pytest.raises(SystemExit):
            query.all_trait_info(self.f, "Trait3")


    def test_non_existing_trait_study_combination(self):
        with pytest.raises(SystemExit):
            query.all_study_info(self.f, "Trait3", "PM002")


    def teardown_method(self, method):
        os.remove(".testfile.h5")


def as_string_set(list):
    my_set = set()
    for element in list:
        my_set.add(str(element))
    return my_set
