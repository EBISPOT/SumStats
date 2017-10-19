import os
import sumstats.chr.loader as loader


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
        frequencyarray = ["3.926e-01", "4.900e-03", "1.912e-01", "7.000e-04"]

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
