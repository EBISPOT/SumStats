import os
import pytest
import sumstats.snp.loader as loader
from tests.prep_tests import *


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

        loader_dictionary = prepare_dictionary()
        loader_dictionary['other'] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", loader_dictionary)

    def test_open_with_None_array(self):

        other_array = None

        loader_dictionary = prepare_dictionary()
        loader_dictionary['other'] = other_array

        with pytest.raises(AssertionError):
            loader.Loader(None, self.h5file, "PM001", loader_dictionary)

    def test_snp_loaded_with_study_snp_not_in_file(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001", loader)

        assert not load.snp_loaded_with_study(snp)

    def test_snp_loaded_with_study_snp_in_file_but_has_no_data(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001", loader)
        load.file.create_group(snp)

        assert not load.snp_loaded_with_study(snp)

    def test_snp_loaded_with_study_snp_in_file_and_has_loaded_data(self):
        snp = 'rs185339560'
        load = prepare_load_object_with_study(self.h5file, "PM001", loader)
        load.load()

        assert load.snp_loaded_with_study(snp)

    def test_is_loaded_only_first_snp_is_loaded_raises_error(self):
        first_snp = 'rs185339560'
        study = 'PM001'
        save_snps_and_study_in_file(self.f, [first_snp], study)
        load = prepare_load_object_with_study(self.h5file, study, loader)

        with pytest.raises(RuntimeError):
            load.is_loaded()

    def test_is_loaded_only_last_snp_loaded_but_not_first(self):
        last_snp = 'rs7085086'
        study = 'PM001'
        save_snps_and_study_in_file(self.f, [last_snp], study)
        load = prepare_load_object_with_study(self.h5file, study, loader)

        with pytest.raises(RuntimeError):
            load.is_loaded()

    def test_is_loaded_returns_false_for_no_snps_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        assert not load.is_loaded()

    def test_is_loaded_returns_true_for_snps_loaded(self):
        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()
        assert load.is_loaded()

