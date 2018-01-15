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

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')
        self.loader_dictionary = prepare_dictionary()

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        other_array = []
        self.loader_dictionary['other'] = other_array
        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", self.loader_dictionary)

    def test_open_with_None_array(self):

        other_array = None

        self.loader_dictionary['other'] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", self.loader_dictionary)

    def test_create_dataset(self):
        random_group = self.f.create_group("random_group")
        data = ['string 1', 'str2']
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 2
        assert dataset[0] == data[0]
        assert dataset[1] == data[1]

        data = [1, 2]
        dset_name = BP_DSET
        gu.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 2
        assert dataset[0] == data[0]
        assert dataset[1] == data[1]

        data = [0.2, 0.3]
        dset_name = OR_DSET
        gu.create_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 2
        assert dataset[0] == data[0]
        assert dataset[1] == data[1]

        dset_name = "random name"
        with pytest.raises(KeyError):
            gu.create_dataset(random_group, dset_name, data)

    def test_expand_dataset(self):
        random_group = self.f.create_group("random group")

        data = ['string1', 'str2']
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, data)
        data2 = ['string3', 'random string']
        loader.expand_dataset(random_group, dset_name, data2)

        dataset = random_group.get(dset_name)
        assert dataset is not None
        assert len(dataset) == 4
        dset_data = dataset[:]
        assert dset_data[0] == data[0]
        assert dset_data[1] == data[1]
        assert dset_data[2] == data2[0]
        assert dset_data[3] == data2[1]

        data = [1, 2]
        dset_name = CHR_DSET
        gu.create_dataset(random_group, dset_name, data)
        data2 = [3, 4]
        loader.expand_dataset(random_group, dset_name, data2)

        dataset = random_group.get(dset_name)
        assert dataset is not None
        assert len(dataset) == 4
        dset_data = dataset[:]
        assert dset_data[0] == data[0]
        assert dset_data[1] == data[1]
        assert dset_data[2] == data2[0]
        assert dset_data[3] == data2[1]

        data = [0.1, 0.2]
        dset_name = MANTISSA_DSET
        gu.create_dataset(random_group, dset_name, data)
        data2 = [0.3, 0.4]
        loader.expand_dataset(random_group, dset_name, data2)

        dataset = random_group.get(dset_name)
        assert dataset is not None
        assert len(dataset) == 4
        dset_data = dataset[:]
        assert dset_data[0] == data[0]
        assert dset_data[1] == data[1]
        assert dset_data[2] == data2[0]
        assert dset_data[3] == data2[1]

    def test_expand_not_existing_dataset(self):
        random_group = self.f.create_group("random group")

        data = ['random string']
        dset_name = STUDY_DSET
        loader.expand_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)

        assert dset is not None
        dset_data = dset[:]
        assert len(dset_data) == 1
        assert dset_data[0] == data[0]

        data2 = ['random string 2']
        loader.expand_dataset(random_group, dset_name, data2)
        dset = random_group.get(dset_name)
        dset_data = dset[:]
        assert len(dset_data) == 2
        assert dset_data[1] == data2[0]

    def test_create_groups_in_parent(self):
        array_of_chromosomes = ["1", 2, "X"]
        load = loader.Loader(None, self.h5file, "PM001", self.loader_dictionary)
        load._create_groups_in_file(array_of_chromosomes)
        chr1 = self.f.get("1")
        assert chr1 is not None
        chr2 = self.f.get("2")
        assert chr2 is not None
        chrX = self.f.get("X")
        assert chrX is not None

    def test_slice_datasets_where_chromosome(self):

        self.loader_dictionary[CHR_DSET] = Dataset([1, 1, 2, 2])
        self.loader_dictionary[SNP_DSET] = Dataset(['snp1', 'snp2', 'snp3', 'snp4'])

        load = loader.Loader(None, self.h5file, "PM001", self.loader_dictionary)
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

    # def test_already_loaded_chromosome_not_there(self):
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     assert not load.already_loaded()
    #
    # def test_already_loaded_block_group_with_no_data(self):
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     load.load()
    #     bparray_new = [1, 1, 1, 1]
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray_new,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     assert not load.already_loaded()
    #
    # def test_already_loaded_study_not_loaded(self):
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     load.load()
    #
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM001', dict)
    #     assert not load.already_loaded()
    #
    # def test_already_loaded_study_already_loaded(self):
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     load.load()
    #
    #     dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
    #             "effect": effectarray, "other": otherarray, 'freq': frequencyarray}
    #
    #     load = loader.Loader(None, self.h5file, 'PM003', dict)
    #     assert load.already_loaded()
