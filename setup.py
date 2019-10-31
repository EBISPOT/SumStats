from distutils.core import setup

setup(
    name='eqtl-sumstats',
    version='0.1.0',
    packages=['sumstats', 'sumstats.utils', 'sumstats.server', 'sumstats.study', 'sumstats.study.search', 'sumstats.study.search.access', 'sumstats.trait', 'sumstats.trait.search',
              'sumstats.trait.search.access', 'sumstats.chr', 'sumstats.chr.search', 'sumstats.chr.search.access', 'config', 'sumstats.errors'],
    entry_points={
        "console_scripts": ['eqtl-load = sumstats.load:main',
                            'eqtl-search = sumstats.controller:main',
                            'eqtl-explore = sumstats.explorer:main',
                            'eqtl-rebuild-snps = sumstats.utils.vcf_to_sqlite:main',
                            'eqtl-prep-file = sumstats.utils.split_by_chrom:main',
                            'eqtl-reindex = sumstats.reindex:main',
                            'eqtl-delete = sumstats.deleter:main']
    },
    url='https://github.com/EBISPOT/SumStats',
    license='',
    description='Package for saving and querying large eqtl summary statistics'
)
