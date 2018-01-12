import os
import pytest
import sumstats.snp.loader as loader
from tests.snp.test_constants import *
import sumstats.utils.group as gu


class TestUnitLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):
        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode='a')

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_open_with_empty_array(self):
        other_array = []

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array, 'freq': frequencyarray}

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", dict)

    def test_open_with_None_array(self):

        other_array = None

        dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
                "effect": effectarray, "other": other_array}

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", dict)

    def test_create_dataset(self):
        random_group = self.f.create_group("random_group")
        data = 'string1'
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, [data])
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        data = 1
        dset_name = BP_DSET
        gu.create_dataset(random_group, dset_name, [data])
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        data = 0.2
        dset_name = OR_DSET
        gu.create_dataset(random_group, dset_name, [data])
        dset = random_group.get(dset_name)
        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == data

        dset_name = "random name"
        with pytest.raises(KeyError):
            gu.create_dataset(random_group, dset_name, [data])

    def test_expand_dataset(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        gu.create_dataset(random_group, dset_name, [data])
        data2 = 'random string4'
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == 'string1'
        assert dataset[1] == 'random string4'

        data = 1
        dset_name = CHR_DSET
        gu.create_dataset(random_group, dset_name, [data])
        data2 = 2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == data
        assert dataset[1] == data2

        data = 0.1
        dset_name = MANTISSA_DSET
        gu.create_dataset(random_group, dset_name, [data])
        data2 = 0.2
        loader.expand_dataset(random_group, dset_name, data2)

        dset = random_group.get(dset_name)
        assert dset is not None
        assert len(dset) == 2
        dataset = dset[:]
        assert dataset[0] == data
        assert dataset[1] == data2

    def test_expand_not_existing_dataset(self):
        random_group = self.f.create_group("random group")

        data = 'string1'
        dset_name = STUDY_DSET
        loader.expand_dataset(random_group, dset_name, data)
        dset = random_group.get(dset_name)

        assert dset is not None
        dataset = dset[:]
        assert len(dataset) == 1
        assert dataset[0] == 'string1'

        data2 = 'str2'
        loader.expand_dataset(random_group, dset_name, data2)
        dset = random_group.get(dset_name)
        dataset = dset[:]
        assert len(dataset) == 2

    def test_snp_loaded_with_study_snp_not_in_file(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001")

        assert not load.snp_loaded_with_study(snp)

    def test_snp_loaded_with_study_snp_in_file_but_has_no_data(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001")
        load.file.create_group(snp)

        assert not load.snp_loaded_with_study(snp)

    def test_snp_loaded_with_study_snp_in_file_and_has_loaded_data(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001")
        load.load()

        assert load.snp_loaded_with_study(snp)

    def test_is_loaded_only_first_snp_is_loaded_raises_error(self):
        first_snp = 'rs185339560'
        study = 'PM001'
        save_snps_and_study_in_file(self.f, [first_snp], study)
        load = prepare_load_object_with_study(self.h5file, study)

        with pytest.raises(RuntimeError):
            load.is_loaded()

    def test_is_loaded_only_last_snp_loaded_but_not_first(self):
        last_snp = 'rs7085086'
        study = 'PM001'
        save_snps_and_study_in_file(self.f, [last_snp], study)
        load = prepare_load_object_with_study(self.h5file, study)

        with pytest.raises(RuntimeError):
            load.is_loaded()

    def test_is_loaded_returns_false_for_no_snps_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001')
        assert not load.is_loaded()

    def test_is_loaded_returns_true_for_snps_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001')
        load.load()
        assert load.is_loaded()


def prepare_load_object_with_study(h5file, study):
    dict = {"snp": snpsarray, "pval": pvalsarray, "chr": chrarray, "or": orarray, "bp": bparray,
            "effect": effectarray, "other": otherarray, 'freq': frequencyarray}

    return loader.Loader(None, h5file, study, dict)


def save_snps_and_study_in_file(opened_file, list_of_snps, study):
    for snp in list_of_snps:
        group = opened_file.create_group(snp)
        gu.create_dataset(group, 'study', [study])