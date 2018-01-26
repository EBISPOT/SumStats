import os
import pytest
import sumstats.chr.loader as loader
from tests.prep_tests import *
from sumstats.utils.dataset import Dataset
import sumstats.utils.group as gu
from sumstats.chr.constants import *


class TestUnitLoader(object):
    h5file = ".testfile.h5"
    f = None
    study = 'PM001'

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')
        self.loader_dictionary = prepare_dictionary()

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        other_array = []
        self.loader_dictionary[OTHER_DSET] = other_array
        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, self.study, self.loader_dictionary)

    def test_open_with_None_array(self):

        other_array = None

        self.loader_dictionary[OTHER_DSET] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, self.study, self.loader_dictionary)

    def test_slice_datasets_where_chromosome(self):

        self.loader_dictionary[CHR_DSET] = Dataset([1, 1, 2, 2])
        self.loader_dictionary[SNP_DSET] = Dataset(['snp1', 'snp2', 'snp3', 'snp4'])

        load = loader.Loader(None, self.h5file, self.study, self.loader_dictionary)
        datasets = load._slice_datasets_where_chromosome(1)

        assert len(datasets[CHR_DSET]) == 2
        assert set(datasets[CHR_DSET]).pop() == 1

        assert len(datasets[SNP_DSET]) == 2
        assert "snp1" in datasets[SNP_DSET]
        assert "snp2" in datasets[SNP_DSET]
        assert "snp3" not in datasets[SNP_DSET]
        assert "snp4" not in datasets[SNP_DSET]

    def test_initialize_block_limits(self):
        floor, ceil = loader.initialize_block_limits()
        assert floor == 0
        assert ceil == BLOCK_SIZE

    def test_increment_block_limits(self):
        floor, ceil = loader.increment_block_limits(BLOCK_SIZE)

        assert floor == BLOCK_SIZE + 1
        assert ceil == 2 * BLOCK_SIZE

    def test_increment_block_limits_twice(self):
        floor, ceil = loader.increment_block_limits(BLOCK_SIZE)
        floor, ceil = loader.increment_block_limits(ceil)

        assert floor == 2 * BLOCK_SIZE + 1
        assert ceil == 3 * BLOCK_SIZE

    def test_block_limit_not_reached_max(self):
        max_bp = 49129966

        notreached = loader.block_limit_not_reached_max(0, max_bp)
        assert notreached

        notreached = loader.block_limit_not_reached_max(max_bp, max_bp)
        assert notreached

        notreached = loader.block_limit_not_reached_max(max_bp + BLOCK_SIZE - 1, max_bp)
        assert notreached

        notreached = loader.block_limit_not_reached_max(max_bp + BLOCK_SIZE, max_bp)
        assert notreached

        notreached = loader.block_limit_not_reached_max(max_bp + BLOCK_SIZE + 1, max_bp)
        assert not notreached

    def test_block_loaded_with_study_chr_missing(self):
        load = prepare_load_object_with_study(self.h5file, self.study, loader)
        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        assert not load._is_block_loaded_with_study(3, 1118275)

    def test_block_loaded_with_study_block_missing(self):
        load = prepare_load_object_with_study(self.h5file, self.study, loader)
        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        assert not load._is_block_loaded_with_study(1, 3118275)

    def test_block_loaded_with_study_study_missing(self):
        load = prepare_load_object_with_study(self.h5file, self.study, loader)
        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        assert not load._is_block_loaded_with_study(1, 1118275)

    def test_block_loaded_with_study(self):
        load = prepare_load_object_with_study(self.h5file, self.study, loader)
        load.load()
        # chrarray = [1, 1, 2, 2]
        # bparray = [1118275, 1120431, 49129966, 48480252]
        assert load._is_block_loaded_with_study(1, 1118275)

    def test_is_loaded_only_first_block_is_loaded_raises_error(self):
        study = self.study

        loader_dictionary = {SNP_DSET: [snpsarray[0]], PVAL_DSET: [pvalsarray[0]], CHR_DSET: [chrarray[0]],
                             OR_DSET: [orarray[0]], BP_DSET: [bparray[0]],
                            EFFECT_DSET: [effectarray[0]], OTHER_DSET: [otherarray[0]], FREQ_DSET: [frequencyarray[0]]}

        load = loader.Loader(None, self.h5file, self.study, loader_dictionary)
        load.load()

        load = prepare_load_object_with_study(self.h5file, study, loader)

        with pytest.raises(RuntimeError):
            load._is_loaded()

    def test_is_loaded_only_last_block_is_loaded_raises_error(self):
        study = self.study

        loader_dictionary = {SNP_DSET: [snpsarray[-1]], PVAL_DSET: [pvalsarray[-1]], CHR_DSET: [chrarray[-1]],
                             OR_DSET: [orarray[-1]], BP_DSET: [bparray[-1]],
                             EFFECT_DSET: [effectarray[-1]], OTHER_DSET: [otherarray[-1]],
                             FREQ_DSET: [frequencyarray[-1]]}

        load = loader.Loader(None, self.h5file, self.study, loader_dictionary)
        load.load()

        load = prepare_load_object_with_study(self.h5file, study, loader)

        with pytest.raises(RuntimeError):
            load._is_loaded()

    def test_is_loaded_returns_false_for_no_blocks_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        assert not load._is_loaded()

    def test_is_loaded_returns_true_for_all_blocks_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)

        assert load._is_loaded()