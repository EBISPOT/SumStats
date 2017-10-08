# SumStats
Summary statistics with HDF5


# Installation - using Docker

Docker documentation: https://docs.docker.com

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Build the docker image
  - `docker build -t sumstats`
- Create the directories that will be used a volumes
  - `mkdir -p files/h5files`
  - `mkdir files/toload`
- Create the container from the <sumstats> image
  - `docker run -i -v $(pwd)/files:/application/files -t myapp`
  
You should be able to see the sumstats packages in the container and run the scripts.

Files to be loaded should be placed in the files/toload volume

Files produced by the sumstats package (.h5 files) should be generated in the files/h5files volume


# Installation - using pip install

- Clone the repository
  - `git clone https://github.com/EBISPOT/SumStats.git`
  - `cd SumStats`
- Install the sumstats package -  this will install h5py, numpy, flask, cherrypy - and sumstats
  - `pip install .`
- Create the directories that will be used to hold the files to be loaded and the .h5 output files
  - `mkdir -p files/h5files`
  - `mkdir files/toload`
