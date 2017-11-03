# import os
# import sumstats.chr.loader as loader
# from tests.chr.test_constants import *
#
#
# class TestSearcher(object):
#     h5file = ".testfile.h5"
#     f = None
#
#     def setup_method(self, method):
#         chrarray1 = [10, 10, 10, 10]
#
#         dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray1, "or": orarray, "bp": bparray,
#                 "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
#
#         load = loader.Loader(None, self.h5file, "PM001", dict)
#         load.load()
#
#     def teardown_method(self, method):
#         os.remove(self.h5file)
#
#     def test_main(self):
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp 1118275:49180252 "
#                            "-pval 4.4:7 -study PM001")
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp 1118275:49180252 "
#                            "-pval :7 -study PM001")
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp 1118275:49180252 "
#                            "-pval 4.4: -study PM001")
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp 1118275:49180252")
#
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp :49180252")
#
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10 -bp 1118275:")
#
#         assert result == 0
#
#         result = os.system("python3 sumstats/chr/searcher.py -h5file .testfile.h5 -chr 10")
#
#         assert result == 0
