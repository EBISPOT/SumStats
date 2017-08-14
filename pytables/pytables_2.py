from tables import *
import numpy as np
from numpy import genfromtxt
import argparse
import hashlib

parser = argparse.ArgumentParser()
parser.add_argument('CSV_input_file', help = 'The file to be loaded')
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file')
parser.add_argument('study_name', help = 'The name of the first group this will belong to')
parser.add_argument('trait_name', help = 'The name of the trait the SNPs of this file are related to')
parser.add_argument('delimiter', help = 'The csv file delimiter')
args = parser.parse_args()

csvf = args.CSV_input_file
dlm = args.delimiter
h5file = args.HDF5_output_file
study = args.study_name
trait = args.trait_name

myarray = genfromtxt(csvf, delimiter = '\t', dtype=None)
print "Loaded csv file: ", csvf

myarray.flags.writeable = False
array_hash = "dataset_" + str(hash(myarray.data))
print "File hash: ", array_hash

class SNP(IsDescription):
    #snp = StringCol(16)
    pval = Float64Col()

f = open_file(h5file, mode = "a")

studypath = "/" + study
if f.__contains__(studypath):
    studytraitpath = studypath + "/" + trait
    if f.__contains__(studytraitpath):
        g = f.get_node(studytraitpath)
    else:
        studypath = studypath + "/"
        g = f.create_group(studypath, trait)
else:
    f.create_group("/", study)
    studypath = studypath + "/"
    g = f.create_group(studypath, trait)

#if g.__contains__(array_hash):
##    g._g_remove(array_hash)
#    print "Array with same hash already exists in the same group. Exiting....."
#    exit()
#else:
#    table = f.create_table(g,array_hash, SNP)
##table = f.create_table(g, array_hash, SNP)


#snp = table.row

path = studypath + "/" + trait + "/"
for i in range(1,22):
    f.create_group(path, "ch" + str(i))

for x,y in np.ndenumerate(myarray):
    try:
        g = f.get_node(path + "/" + "ch" + str(y[2]))
        table = f.create_table(g, y[0], SNP)
    except NodeError:
        print y[0] + " already exists!"
    snp = table.row
    #snp['snp'] = y[0]
    snp['pval'] = float(y[1])
    snp.append()
    table.flush()

 
