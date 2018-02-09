import os

import sumstats.trait.loader as loader
from tests.prep_tests import *
from sumstats.trait.constants import *


class TestLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM001', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM002', trait='Trait1', loader=loader)
        load.load()

        load = prepare_load_object_with_study_and_trait(h5file=self.h5file, study='PM003', trait='Trait2', loader=loader)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_trait_groups(self):
        trait_1 = self.f.get("Trait1")
        assert trait_1 is not None
        assert len(trait_1.keys()) == 2

        trait_2 = self.f.get("Trait2")
        assert trait_2 is not None
        assert len(trait_2.keys()) == 1

        trait_3 = self.f.get("Trait3")
        assert trait_3 is None

    def test_study_groups(self):
        trait_1 = self.f.get("Trait1")

        study_1 = trait_1.get("PM001")
        assert study_1 is not None
        assert study_1.name == "/Trait1/PM001"

        assert len(study_1.keys()) != 0

        study_2 = trait_1.get("PM001")
        assert len(study_2.keys()) != 0

        trait_2 = self.f.get("Trait2")

        studies = list(trait_2.keys())
        assert len(studies) == 1

        assert studies[0] == "PM003"

    def test_datasets_in_studies(self):
        study_1 = self.f.get("/Trait1/PM001")
        dsets = list(study_1.keys())

        assert len(dsets) == len(TO_STORE_DSETS)
        assert study_1.get(SNP_DSET) is not None
        assert study_1.get(CHR_DSET) is not None
        assert study_1.get(BP_DSET) is not None
        assert study_1.get(MANTISSA_DSET) is not None
        assert study_1.get(EXP_DSET) is not None

        study_2 = self.f.get("/Trait1/PM001")
        dsets = list(study_2.keys())

        assert len(dsets) == len(TO_STORE_DSETS)
        assert study_1.get(SNP_DSET) is not None
        assert study_1.get(CHR_DSET) is not None
        assert study_1.get(BP_DSET) is not None
        assert study_1.get(MANTISSA_DSET) is not None
        assert study_1.get(EXP_DSET) is not None

        study_3 = self.f.get("/Trait2/PM003")
        dsets = list(study_3.keys())

        assert len(dsets) == len(TO_STORE_DSETS)
        assert study_1.get(SNP_DSET) is not None
        assert study_1.get(CHR_DSET) is not None
        assert study_1.get(BP_DSET) is not None
        assert study_1.get(MANTISSA_DSET) is not None
        assert study_1.get(EXP_DSET) is not None

    def test_study_group_dsets_content(self):
        study_1 = self.f.get("/Trait1/PM001")
        assert study_1 is not None
        info = list(study_1.keys())
        assert len(info) == len(TO_STORE_DSETS)

        mantissa = study_1.get(MANTISSA_DSET)
        assert len(mantissa[:]) == 4
        assert mantissa[:][0] == 4.865

        exp = study_1.get(EXP_DSET)
        assert len(exp[:]) == 4
        assert exp[:][0] == -1
