from tables import *
import numpy as np
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file')
parser.add_argument('study_name', help = 'The study I am looking for')
parser.add_argument('trait_name', help = 'The trait I am looking for')
args = parser.parse_args()

h5file = args.HDF5_output_file 
study = args.study_name 
trait = args.trait_name

class SNP(IsDescription):
    snp = StringCol(16)
    pval = Float64Col()

f = open_file(h5file, mode = "r")

group = f.get_node("/" + study + "/" + trait)

for child in group._v_children:
    table = f.get_node("/" + study + "/" + trait + "/" + child)

    for x in table.iterrows():
        if x['snp'] == "rs76947912":
            print x['snp'], x['pval']
		

