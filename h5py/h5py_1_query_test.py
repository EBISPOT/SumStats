import h5py
import os
import unittest
import h5py_1 as loader
import h5py_1_query as query


def main():
    unittest.main()


class TestFirstApproach(unittest.TestCase):

    h5file = ".testfile.h5"
    f = None

    def setUp(self, h5file=h5file):

        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = [0.4865, 0.4314, 0.5986, 0.7057]
        chrarray1 = [10, 10, 10, 10]
        chrarray2 = [9, 9, 9, 9]
        orarray = [0.92090, 1.01440, 0.97385, 0.99302]

        load = loader.Loader(None, h5file, "PM001", "Trait1", snpsarray, pvalsarray, chrarray1, orarray)
        load.load()
        load = loader.Loader(None, h5file, "PM002", "Trait1", snpsarray, pvalsarray, chrarray2, orarray)
        load.load()
        load = loader.Loader(None, h5file, "PM003", "Trait2", snpsarray, pvalsarray, chrarray1, orarray)
        load.load()

        # open h5 file in read mode
        self.f = h5py.File(h5file, mode="r")

    def test_query_1_retrieve_all_information_for_trait_1(self):
        info_array = query.all_trait_info(self.f, "Trait1")
        snps = info_array[:,0]
        self.assertTrue(len(snps) == 8, "Trait 1 has 8 SNPS loaded in 2 studies")

        studies = info_array[:,4]
        study_set = as_string_set(studies)

        self.assertTrue(study_set.__len__() == 2, "Trait 1 has 2 studies")

    def test_query_1_retrieve_all_information_for_trait_2(self):

        info_array = query.all_trait_info(self.f, "Trait2")
        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4, "Trait 2 has 4 SNPS loaded in 1 study")

        studies = info_array[:,4]
        study_set = as_string_set(studies)

        self.assertTrue(study_set.__len__() == 1, "Trait 1 has 1 study")

    def test_query_2_retrieve_all_info_for_study_PM001(self):

        info_array = query.all_study_info(self.f, "Trait1", "PM001")

        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4, "Each study loaded has 4 snps")

        studies = info_array[:,4]
        study_set = as_string_set(studies)

        self.assertTrue(study_set.__len__() == 1, "We asked for 1 study, we should get 1 study")
        self.assertTrue("PM001" in study_set.pop(), "We asked for study PM001")

    def test_query_3_get_info_for_snp_rs185339560(self):

        info_array = query.all_snp_info(self.f, "rs185339560")
        snps = info_array[:,0]
        snp_set = as_string_set(snps)

        self.assertTrue(snp_set.__len__() == 1, "Should only have one unique SNP id")
        self.assertTrue(snp_set.pop() == "rs185339560")

        self.assertTrue(len(info_array) == 3, "info_array should have 3 rows, since we loaded each SNP in 3 "
                                              "study/trait combinations")

        pvals = info_array[:,1]
        self.assertTrue(pvals[0] == pvals[1] == pvals[2], "We should have 3 pvalues and they should all be the same "
                                                          "because we loaded the same dataset 3 times")

        studies = info_array[:,4]
        self.assertTrue("PM001" in studies)
        self.assertTrue("PM002" in studies)
        self.assertTrue("PM003" in studies)

    def test_query_4_get_info_for_chromosome_10(self):

        info_array = query.all_chromosome_info(self.f, 10)
        snps = info_array[:,0]
        self.assertTrue(len(snps) == 8)

        chromosomes = info_array[:,2]
        chr_set = as_string_set(chromosomes)

        self.assertTrue(chr_set.__len__() == 1)
        self.assertTrue(chr_set.pop() == "10")

        studies = info_array[:,4]
        self.assertFalse("PM002" in studies)
        self.assertTrue("PM001" in studies)
        self.assertTrue("PM003" in studies)

    def test_query_4_get_info_for_chromosome_9(self):

        info_array = query.all_chromosome_info(self.f, 9)
        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4)

        chromosomes = info_array[:,2]
        chr_set = as_string_set(chromosomes)

        self.assertTrue(chr_set.__len__() == 1)
        self.assertTrue(chr_set.pop() == "9")

        studies = info_array[:,4]
        self.assertFalse("PM001" in studies)
        self.assertTrue("PM002" in studies)
        self.assertFalse("PM003" in studies)

    def test_query_5_get_all_info_for_snp_rs185339560_and_Trait1(self):

        info_array = query.all_snp_info(self.f, "rs185339560", "Trait1")
        studies = info_array[:,4]
        # Study - Trait
        # PM001 - Trait1
        # PM002 - Trait1
        # PM003 - Trait2
        self.assertFalse("PM003" in studies)
        self.assertTrue("PM001" in studies)
        self.assertTrue("PM002" in studies)

        snps = info_array[:,0]
        snp_set = as_string_set(snps)

        self.assertTrue(snp_set.__len__() == 1, "Should only have one unique SNP id")
        self.assertTrue(snp_set.pop() == "rs185339560")

    # Study - Trait - Chromosome
    # PM001 - Trait1 - 10
    # PM002 - Trait1 - 9
    # PM003 - Trait2 - 10

    def test_query_6_all_info_for_chromosome_9_and_trait(self):

        info_array = query.all_chromosome_info(self.f, "9", "Trait1")
        study = info_array[:,4]
        self.assertTrue("PM002" in study)
        self.assertFalse("PM001" in study)
        self.assertFalse("PM003" in study)

        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4)

        info_array = query.all_chromosome_info(self.f, "9", "Trait2")
        self.assertTrue(len(info_array) == 0, "Combination chromosome 9, Trait2 should return nothing")

    def test_query_6_all_info_for_chromosome_10_and_trait(self):

        info_array = query.all_chromosome_info(self.f, "10", "Trait1")
        study = info_array[:,4]
        self.assertTrue("PM001" in study)
        self.assertFalse("PM003" in study)
        self.assertFalse("PM002" in study)

        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4)

        info_array = query.all_chromosome_info(self.f, "10", "Trait2")
        study = info_array[:,4]
        self.assertTrue("PM003" in study)
        self.assertFalse("PM001" in study)
        self.assertFalse("PM002" in study)

        snps = info_array[:,0]
        self.assertTrue(len(snps) == 4)

    def test_retrieve_all_info(self):
        info_array = query.retrieve_all_info(self.f)
        snps = info_array[:, 0]
        self.assertTrue(len(snps) == 12)

        studies = info_array[:,4]
        self.assertTrue("PM001" in studies)
        self.assertTrue("PM003" in studies)
        self.assertTrue("PM002" in studies)

        chroms = info_array[:,2]
        self.assertTrue("9" in chroms)
        self.assertTrue("10" in chroms)

        snps_set = as_string_set(snps)
        self.assertTrue(snps_set.__len__() == 4)

    def test_retrieve_all_info_from_study(self):
        study_group = self.f.get("/Trait1/PM001")
        info_array =  query.retrieve_all_info_from_study("PM001", study_group)
        self.assertTrue(len(info_array) == 4)

    def test_non_existing_trait(self):
        with self.assertRaises(SystemExit) as cm:
            query.all_trait_info(self.f, "Trait3")

        self.assertEqual(cm.exception.code, 1)

    def test_non_existing_trait_study_combination(self):
        with self.assertRaises(SystemExit) as cm:
            query.all_study_info(self.f, "Trait3", "PM002")

        self.assertEqual(cm.exception.code, 1)

    def tearDown(self, h5file=h5file):
        os.remove(h5file)


def as_string_set(list):
    my_set = set()
    for element in list:
        my_set.add(str(element))
    return my_set


if __name__ == "__main__":
    main()