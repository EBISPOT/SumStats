from distutils.core import setup

setup(
    name='sumstats',
    version='0.1-SNAPSHOT',
    packages=['sumstats', 'sumstats.utils', 'sumstats.server', 'sumstats.trait', 'sumstats.trait.search',
              'sumstats.trait.search.access', 'sumstats.chr', 'sumstats.chr.search', 'sumstats.chr.search.access',
              'sumstats.snp', 'sumstats.snp.search', 'sumstats.snp.search.access', 'config', 'sumstats.errors'],
    entry_points={
        "console_scripts": ['gwas-load = sumstats.load:main',
                            'gwas-search = sumstats.search:main',
                            'gwas-explore = sumstats.explorer:main',
                            'gwas-server = sumstats.server.app:main']
    },
    url='https://github.com/EBISPOT/SumStats',
    license='',
    author='Olga Vrousgou',
    author_email='olgavrou@gmail.com',
    description='Package for saving and querying large summary statistics',
    install_requires=['pandas', 'flask', 'simplejson']
)
