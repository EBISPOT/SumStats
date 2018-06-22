import os
import shutil
import pytest
import sumstats.snp.loader as loader
from tests.prep_tests import *
from sumstats import load as load


class TestCommandLineLoader(object):

    def setup_method(self):
        os.makedirs('./output/bysnp/1')
        output_location = './output/bysnp/'
        h5file = output_location + '/1/file_1.h5'

        load = prepare_load_object_with_study(h5file, 'PM001', loader)
        load.load()

        load = prepare_load_object_with_study(h5file, 'PM002', loader)
        load.load()

        load = prepare_load_object_with_study(h5file, 'PM003', loader)
        load.load()

    def teardown_method(self):
        shutil.rmtree('./output')

    def test_loader_missing_required(self):
        with pytest.raises(SystemExit):
            load.argument_parser(['-tsv', 'a/path/to/a/file'])