import os
import pytest
import shutil
import numpy as np
from sumstats.utils import filesystem_utils as fsu


class TestUnitUtils(object):

    dir_name = '.test_dir'
    file1 = 'file_EFO_0000384.h5'
    f1 = dir_name + '/' + file1
    f2 = dir_name + '/file_EFO_0000729.h5'
    f3 = dir_name + '/file_EFO_0001360.h5'
    f4 = dir_name + '/file_EFO_0003767.h5'
    f5 = dir_name + '/file_EFO_0004305.h5'
    f6 = dir_name + '/file_EFO_0004326.h5'

    def setup_method(self):
        # create all the files in a directory
        os.makedirs(self.dir_name)
        open(self.f1, 'a').close()
        open(self.f2, 'a').close()
        open(self.f3, 'a').close()
        open(self.f4, 'a').close()
        open(self.f5, 'a').close()
        open(self.f6, 'a').close()

    def teardown_method(self):
        shutil.rmtree(self.dir_name)

    def test_get_h5files_in_dir_same_order(self):
        files1 = fsu.get_h5files_in_dir('./', self.dir_name)
        files2 = fsu.get_h5files_in_dir('./', self.dir_name)
        assert np.array_equal(files1, files2)

    def test_get_h5files_in_dir_raise_error(self):
        with pytest.raises(RuntimeError):
            fsu.get_h5files_in_dir('/', self.dir_name)

    def test_get_file_path(self):
        file_path = fsu.get_file_path(self.dir_name, self.file1)
        assert file_path == self.f1

    def test_get_file_path_raises_error(self):
        with pytest.raises(RuntimeError):
            fsu.get_file_path(self.dir_name, self.f1)