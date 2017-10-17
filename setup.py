from distutils.core import setup

setup(
    name='sumstats',
    version='0.1-SNAPSHOT',
    packages=['sumstats', 'sumstats.utils', 'sumstats.server', 'sumstats.trait', 'sumstats.chr'],
    url='https://github.com/EBISPOT/SumStats',
    license='',
    author='Olga Vrousgou',
    author_email='olgavrou@gmail.com',
    description='Package for saving and querying large summary statistics',
    install_requires=['h5py==2.7.0', 'numpy>=1.12.1', 'pandas', 'pyyaml', 'flask==0.12.2', 'cherrypy==11.0.0']
)
