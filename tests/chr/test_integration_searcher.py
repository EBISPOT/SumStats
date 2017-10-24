import os
import sumstats.chr.loader as loader
from tests.chr.test_constants import *

class TestFirstApproach(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        chrarray1 = [10, 10, 10, 10]

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray1, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

        load = loader.Loader(None, self.h5file, "PM001", dict)
        load.load()

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_main(self):
        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 1 -chr 10 -bl 1118275 -bu "
                           "49180252 -pl 4.4 -pu 7 -study PM001")
        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 1 -chr 10 -bl 1118275 -bu "
                           "49180252")

        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 1 -chr 10 -bl 1118275")

        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 1 -chr 10 -bu 1118275")

        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 2 -snp rs185339560 -chr 10 "
                           "-pl 4.4 -pu 7 -study PM001")
        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 2 -snp rs185339560 -chr 10 "
                           "-bl 1118275")

        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 2 -snp rs185339560 -chr 10 "
                           "-bu 1118275")

        assert result == 0

        result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -query 1 -chr 10")

        assert result == 0
