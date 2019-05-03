import pandas as pd
import tables as tb
import subprocess
import os
import glob
import re
from collections import defaultdict
from sumstats.common_constants import *
from sumstats.utils.properties_handler import properties
from sumstats.utils import properties_handler
from sumstats.utils import filesystem_utils as fsutils
import sumstats.utils.sqlite_client as sq 


def main():
    properties_handler.set_properties()  # pragma: no cover
    h5files_path = properties.h5files_path # pragma: no cover
    loaded_files_path = properties.loaded_files_path  # pragma: no cover
    study_dir = properties.study_dir
    snp_dir = properties.snp_dir
    database = properties.sqlite_path

    hdfs = glob.glob(os.path.join(self.search_path, self.study_dir) + "/[1-25]/*.h5")
    

    for f in hdfs:
        with tb.open_file(f, mode = "r") as table:

            filename = None
            study = None
            traits = []



if __name__ == "__main__":
    main()  # pragma: no cover
