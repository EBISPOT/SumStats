import h5py
import numpy as np
from numpy import genfromtxt
import argparse
import hashlib
from operator import itemgetter
import math

parser = argparse.ArgumentParser()
parser.add_argument('CSV_input_file', help = 'The file to be loaded')
parser.add_argument('HDF5_output_file', help = 'The name of the HDF5 file to be created/updated')
parser.add_argument('study_name', help = 'The name of the first group this will belong to')
args = parser.parse_args()

csvf = args.CSV_input_file
h5file = args.HDF5_output_file
study = args.study_name

pvalarray = genfromtxt(csvf, delimiter = '\t', usecols=(1))
snparray = genfromtxt(csvf, delimiter = '\t', usecols=(0), dtype=object)

print "Loaded csv file: ", csvf

f = h5py.File(h5file, 'a')

# Create my compound type triple to be stored in the hash_table
vlen = h5py.special_dtype(vlen=str)
dt = np.dtype([("snp", vlen), ("pval", np.float32), ("study", vlen)])

def snp_hash(snp):
    p = 53
    N = 1123

    # Map A -> 0 ... a -> 26 ... z -> 51
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') if c.islower() else ord(c) - ord('A') - 6 for c in snp]

    h = sum(pow(p, i) * s for i, s in enumerate(SNP))

    return h % N #MODULO


N = 1123
if len(snparray) < N:
    M = len(snparray) + 1
else:
    M = int(len(snparray) / N) + 1123

emptydt = (None, None, None)
dataset = f.get("hash_table")
if dataset is None:
    hash_table = np.empty((N, M), dtype = dt)
    for i in xrange(N):
        for j in xrange(M):
            hash_table[i][j] = emptydt
    hash_table_indexer = np.zeros((N), dtype = int)
    print "Initialized dataset shape:" 
    print hash_table.shape
else:
    hash_table = dataset[:]
    # for each row in hash_table create the row index that holds the number of columns it has filled
    hash_table_indexer = np.zeros((N), dtype = int)
    for i in range(0, len(hash_table)):
        hash_table_indexer[i] = len(hash_table[i,:][[hash_table[i,:]["pval"] > 0]])
    #print "hash table indexer at 714: %s" %( hash_table_indexer[714] )
    # if the number of columns differs with this dataset, expand the hash_table
    max_cols = max(hash_table_indexer)
    if M > max_cols:
        new_rows = M
        hash_table_to_append =  np.empty((N, new_rows), dtype = dt)
        for i in xrange(N):
            for j in xrange(new_rows):
                hash_table_to_append[i][j] = emptydt
        hash_table = np.append(hash_table, hash_table_to_append, 1)
        print "Added new rows"
        print new_rows
    print "Loaded dataset shape: "
    print hash_table.shape

print "Start loading data..."
columns_to_append = ""
for i in range(0, len(snparray)):
    if i % 1000000 == 0:
        print "Loaded %s so far..." % (i)
    snp = snparray[i]
    pval = pvalarray[i]
    
    n = snp_hash(snp)
    m = hash_table_indexer[n]
    to_insert = [(snp, pval, study)]
   
     
    # Insert inserts a column right before the given indice
    try: 
        hash_table[n][m]["snp"] = snp
        hash_table[n][m]["pval"] = pval
        hash_table[n][m]["study"] = study
        hash_table_indexer[n] += 1
    except IndexError:
        print "SHOULD NOT BE HERE!"
        # m is out of bounds, we need to add a column to the hash_table
        new_column = np.empty((N), dtype = dt)
        for element in xrange(N):
            new_column[element] = emptydt
        # expanding the column for row n and adding the new triple there
        new_column[n]["snp"] = snp
        new_column[n]["pval"] = pval        
        new_column[n]["study"] = study     
  
        # to be appended to hash_table
        if len(columns_to_append) == 0:
            columns_to_append = new_column
        else:
            columns_to_append = np.column_stack([columns_to_append, new_column]) 

if len(columns_to_append) != 0:
        hash_table = np.append(hash_table, columns_to_append, 1)

if dataset is None:
    dataset = f.create_dataset('hash_table', data=hash_table, maxshape=(N, None), dtype = dt)
else:
    dataset.resize(hash_table.shape)
    dataset[:] = hash_table
    print "resized"

print "Done!"
