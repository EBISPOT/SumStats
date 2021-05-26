from tests.prep_tests import *
import snakemake


class TestLoader(object):

    def test_snakemake_dryrun(self):
        snakemake_conf_dict = get_load_config()
        snakemake_result = snakemake.snakemake('Snakefile', dryrun=True, config=snakemake_conf_dict)
        assert snakemake_result is True



