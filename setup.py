from distutils.core import setup

setup(
    name='sumstats',
    version='0.1-SNAPSHOT',
    packages=['sumstats', 'sumstats.utils', 'sumstats.server', 'sumstats.study', 'sumstats.study.search', 'sumstats.study.search.access', 'sumstats.trait', 'sumstats.trait.search',
              'sumstats.trait.search.access', 'sumstats.chr', 'sumstats.chr.search', 'sumstats.chr.search.access', 'config', 'sumstats.errors'],
    entry_points={
        "console_scripts": ['gwas-load = sumstats.load:main',
                            'gwas-search = sumstats.controller:main',
                            'gwas-explore = sumstats.explorer:main',
                            'gwas-rebuild-snps = sumstats.utils.rebuild_snps:main',
                            'gwas-reindex = sumstats.reindex:main',
                            'gwas-delete = sumstats.deleter:main']
    },
    url='https://github.com/EBISPOT/SumStats',
    license='',
    author='Olga Vrousgou',
    author_email='olgavrou@gmail.com',
    description='Package for saving and querying large summary statistics',
    install_requires=['pandas==0.19.2', 'tables==3.4.3', 'flask', 'simplejson', 'gunicorn', 'paste', 'numpy==1.15.4', 'eventlet', 'pytest-cov']
)
