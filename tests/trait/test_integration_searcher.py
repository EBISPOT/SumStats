import os
import sumstats.trait.loader as loader
from tests.trait.test_constants import *


class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        chrarray = [10, 10, 10, 10]
        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM001", "Trait1", dict)
        load.load()

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_main(self):
        result = os.system("python3 sumstats/trait/searcher.py -h5file .testfile.h5 -query 1 -trait Trait1 -pu 7.0 "
                           "-pl 4.0 -bl 1118276 -bu 1165309")
        assert result == 0

        result = os.system("python3 sumstats/trait/searcher.py -h5file .testfile.h5 -query 1 -trait Trait1 -study "
                           "PM001 -snp rs185339560")

        assert result == 0

        result = os.system("python3 sumstats/trait/searcher.py -h5file .testfile.h5 -query 1 -trait Trait1 -pu 7.0 "
                           "-pl 4.0 -snp rs185339560")
        assert result == 0

        result = os.system("python3 sumstats/trait/searcher.py -h5file .testfile.h5 -query 1 -trait Trait1 -pu 7.0 "
                           "-pl 4.0 -chr 10")

        assert result == 0

        result = os.system("python3 sumstats/trait/searcher.py -h5file .testfile.h5 -query 2 -trait Trait1 -study "
                           "PM001 -pu 7.0 -pl 4.0 -chr 10")

        assert result == 0
