from tests.prep_tests import *
import pathlib
import snakemake


class TestLoader(object):
    def setup_method(self):
        prepare_load_env_with_test_data()

    def teardown_method(self):
        snakemake_conf_dict = get_load_config()
        self.rmdir(snakemake_conf_dict['loaded'])
        self.rmdir(snakemake_conf_dict['to_load'])
        self.rmdir(snakemake_conf_dict['out_dir'])

    def rmdir(self, directory):
        directory = pathlib.Path(directory)
        for item in directory.iterdir():
            if item.is_dir():
                self.rmdir(item)
            else:
                item.unlink()
        directory.rmdir()

    def test_snakemake_dryrun(self):
        snakemake_conf_dict = get_load_config()
        snakemake_result = snakemake.snakemake('Snakefile', dryrun=True, config=snakemake_conf_dict)
        assert snakemake_result is True

    def test_snakemake_run(self):
        snakemake_conf_dict = get_load_config()
        snakemake_result = snakemake.snakemake('Snakefile', config=snakemake_conf_dict)
        assert snakemake_result is True



