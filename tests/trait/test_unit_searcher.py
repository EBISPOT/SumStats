import os

import pytest

import sumstats.trait.loader as loader
from sumstats.trait.searcher import Search


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        snpsarray = ["rs185339560", "rs11250701", "chr10_2622752_D", "rs7085086"]
        pvalsarray = ["0.4865", "0.4314", "0.5986", "0.7057"]
        chrarray1 = ["10", "10", "10", "10"]
        orarray = ["0.92090", "1.01440", "0.97385", "0.99302"]
        bparray = ["1118275", "1120431", "49129966", "48480252"]
        effectarray = ["A", "B", "C", "D"]
        otherarray = ["Z", "Y", "X", "W"]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray1, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray}

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray1, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray}

        load = loader.Loader(None, self.h5file, "PM002", "Trait1", dict)
        load.load()

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray1, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray}

        load = loader.Loader(None, self.h5file, "PM003", "Trait2", dict)
        load.load()

        self.query = Search(self.h5file)

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_query_for_trait(self):
        name_to_dataset = self.query.query_for_trait("Trait1")
        assert len(name_to_dataset["snp"]) == 8

        study_set = as_string_set(name_to_dataset["study"])

        assert study_set.__len__() == 2

        name_to_dataset = self.query.query_for_trait("Trait2")
        assert len(name_to_dataset["snp"]) == 4

        study_set = as_string_set(name_to_dataset["study"])

        assert study_set.__len__() == 1

    def test_query_for_study(self):
        name_to_dataset = self.query.query_for_study("Trait1", "PM001")

        assert len(name_to_dataset["snp"]) == 4

        study_set = as_string_set(name_to_dataset["study"])

        assert study_set.__len__() == 1
        assert "PM001" in study_set.pop()

        name_to_dataset = self.query.query_for_study("Trait1", "PM001")
        assert len(name_to_dataset["snp"]) == 4

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
