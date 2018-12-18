import os

import sumstats.trait.loader as loader
from tests.prep_tests import *
from sumstats.trait.constants import *
from sumstats.trait.study_deleter import Deleter
from config import properties
import shutil


class TestDeleter(object):
    h5file1 = "./output/bytrait/file_t1.h5"
    h5file2 = "./output/bytrait/file_t2.h5"

    f = None

    def setup_method(self, method):
        os.makedirs('./output/bytrait')

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study='PM001', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file1, study='PM002', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file2, study='PM003', trait='Trait2', loader=loader)
        load.load()

        properties.h5files_path = "./output"
        self.f1 = h5py.File(self.h5file1, mode="r+")
        self.f2 = h5py.File(self.h5file2, mode="r+")
        self.deleter = Deleter(study='PM001', config_properties=properties)

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_trait1_has_one_study_deleted(self):
        trait_1 = self.f1.get("Trait1")
        assert len(trait_1.keys()) == 2
        self.deleter.delete_study()
        assert len(trait_1.keys()) == 1

    def test_trait2_is_unaffected(self):
        self.deleter.delete_study()
        trait_2 = self.f2.get("Trait2")
        assert len(trait_2.keys()) == 1

    def test_trait1_has_correct_study(self):
        self.deleter.delete_study()
        trait_1 = self.f1.get("Trait1")
        study_1 = trait_1.get("PM001")
        study_2 = trait_1.get("PM002")
        assert study_1 is None
        assert study_2 is not None
        assert study_2.name == "/Trait1/PM002"

    def test_non_deleted_trait_datasets_are_unaffected(self):
        self.deleter.delete_study()
        study_2 = self.f1.get("/Trait1/PM002")
        dsets = list(study_2.keys())

        assert len(dsets) == len(TO_STORE_DSETS)
        assert study_2.get(SNP_DSET) is not None
        assert study_2.get(CHR_DSET) is not None
        assert study_2.get(BP_DSET) is not None
        assert study_2.get(MANTISSA_DSET) is not None
        assert study_2.get(EXP_DSET) is not None

        mantissa = study_2.get(MANTISSA_DSET)
        assert len(mantissa[:]) == 4
        assert mantissa[:][0] == 4.865

        exp = study_2.get(EXP_DSET)
        assert len(exp[:]) == 4
        assert exp[:][0] == -1

        study_3 = self.f2.get("/Trait2/PM003")
        dsets = list(study_3.keys())

        assert len(dsets) == len(TO_STORE_DSETS)
        assert study_3.get(SNP_DSET) is not None
        assert study_3.get(CHR_DSET) is not None
        assert study_3.get(BP_DSET) is not None
        assert study_3.get(MANTISSA_DSET) is not None
        assert study_3.get(EXP_DSET) is not None

    def test_delete_trait_if_no_children(self):
        self.deleter = Deleter(study='PM003', config_properties=properties)
        self.deleter.delete_study()
        study_3 = self.f2.get("/Trait2/PM003")
        assert study_3 is None
        trait_2 = self.f2.get("Trait2")
        assert trait_2 is None


