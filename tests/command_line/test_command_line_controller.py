import os
import shutil
import sumstats.snp.loader as loader
from tests.prep_tests import *
from sumstats import controller as controller


class TestCommandLineController(object):

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

    def test_controller(self):
        parser = controller.argument_parser(['-path', './output', '-snp', 'rs185339560'])
        assert parser.path == "./output"
        assert parser.snp == "rs185339560"

    def test_controller_config(self):
        parser = controller.argument_parser(['-config', 'config/properties.json'])
        assert parser.config == "config/properties.json"
