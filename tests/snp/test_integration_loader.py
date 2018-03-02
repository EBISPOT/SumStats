import os
import pytest
import sumstats.snp.loader as loader
from tests.prep_tests import *
from sumstats.snp.constants import *
from sumstats.errors.error_classes import *


class TestLoader(object):
    h5file = ".testfile.h5"
    f = None

    def setup_method(self, method):

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(self.h5file, 'PM003', loader)
        load.load()

        # open h5 file in read/write mode
        self.f = h5py.File(self.h5file, mode="a")

    def teardown_method(self, method):
        os.remove(self.h5file)

    def test_snp_group(self):
        snp_group = self.f.get("/rs185339560")
        assert snp_group is not None

        snp_group = self.f.get("/rs7085086")
        assert snp_group is not None

    def test_snp_group_content(self):
        snp1 = self.f.get("/rs185339560")
        assert snp1 is not None
        info = list(snp1.keys())
        assert len(info) == len(TO_STORE_DSETS)

        chromosome = snp1.get(CHR_DSET)
        assert len(chromosome[:]) == 3  # loaded 3 times for 3 diff studies
        assert chromosome[:][0] == 1

        mantissa = snp1.get(MANTISSA_DSET)
        assert len(mantissa[:]) == 3  # loaded 3 times for 3 diff studies
        assert mantissa[:][0] == 4.865

        exp = snp1.get(EXP_DSET)
        assert len(exp[:]) == 3  # loaded 3 times for 3 diff studies
        assert exp[:][0] == -1

        studies = snp1.get(STUDY_DSET)
        assert len(studies[:]) == 3
        assert studies[:][0] == "PM001"
        assert studies[:][1] == "PM002"
        assert studies[:][2] == "PM003"

    def test_study_already_loaded_raises_error(self):

        load = prepare_load_object_with_study(self.h5file, 'PM001', loader)
        with pytest.raises(AlreadyLoadedError):
            load.load()