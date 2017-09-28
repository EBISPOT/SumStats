import time
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

print(time.strftime('%a %H:%M:%S'))

pvalarray = genfromtxt(csvf, delimiter = '\t', usecols=(1))
snparray = genfromtxt(csvf, delimiter = '\t', usecols=(0), dtype=object)

print "Loaded csv file: ", csvf
print(time.strftime('%a %H:%M:%S'))

f = h5py

# Create my compound type triple to be stored in the hash_table
vlen = h5py.special_dtype(vlen=str)
dt = np.dtype([("snp", vlen), ("pval", np.float32), ("study", vlen)])

# the number of columns for each row, should not change
M = 10000
# the number of rows should double (and go to the next prime) if the columns get full
N = 4007
# set to true if resize is needed
resize = False

def snp_hash(snp):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique chars
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in snp]

    h = sum(pow(p, i) * c for i, c in enumerate(SNP))

    return h % N #MODULO

def next_N_prime(n):
    print "calculating next prime"
    primes = [4007, 8017, 16057, 32117, 64237, 128477, 256957, 513917, 10280863]
    idx = primes.index(n)
    if idx == len(primes) - 1:
        print "We do not support growing the table over 10280863 rows"
        print "Consider expanding the primes table or creating a different file"
        raise SystemExit(1)
    else:
        return primes[idx + 1]


def table_row_expander():
    print "Table will soon be out of bounds, expanding rows and re-organizing data starting..."
    # a row is reaching it's capacity of M entries, need to expand rows and re-distribute the snps
    print "N before:", N
    global N
    N = next_N_prime(N)
    print "N after:", N
    new_hash_table = create_table_with_empty_elements(N, M)
    new_hash_table_indexer = np.zeros((N), dtype = int)
    for row in dataset:
        for element in row:
            snp = element["snp"]
            if snp is "":
                continue
            n = snp_hash(snp)
            m = new_hash_table_indexer[n]
            new_hash_table[n][m]["snp"] = snp
            new_hash_table[n][m]["pval"] = element["pval"]
            new_hash_table[n][m]["study"] = element["study"]
            new_hash_table_indexer[n] += 1
    print "done moving the data"
    global dataset
    dataset.resize((N,M))
    dataset[:] = new_hash_table
    global hash_table_indexer
    hash_table_indexer = new_hash_table_indexer
    global resize
    resize = True
    print "doubled the rows in the table and re-organized tha data..."

def create_table_with_empty_elements(N,M):
    emptydt = (None, 0., None)
    #table = np.array([[emptydt for i in xrange(M)] for j in xrange(N)], dtype = dt)
    table = np.empty((N,M), dtype = dt)
    for i in xrange(N):
        for j in xrange(M):
            table[i][j] = emptydt
    return table

def create_table_row_indexer(table):
    hash_table_indexer = np.zeros((N), dtype = int)
    for i in xrange(len(table)):
        hash_table_indexer[i] = len(table[i,:][[table[i,:]["pval"] > 0]])
    return hash_table_indexer

def get_row_index(row):
    return len(dataset[row,:][[dataset[row,:]["pval"] > 0]])


dset = f.get("hash_table")
if dset is None:
    dataset = create_table_with_empty_elements(N,M)
    # initialize the table indexer to keep the current number of populated columns in each row
    hash_table_indexer = np.zeros((N), dtype = int)
    print "Initialized dataset shape:"
    print dataset.shape
else:
    dataset = dset
    # set current N
    N = dataset.shape[0]
    #for each row in hash_table create the row index that holds the number of columns it has filled
    hash_table_indexer = create_table_row_indexer(dataset)
    # if the number of columns is full we need to double the rows of hash_table and recalculate the hashes
    max_cols = max(hash_table_indexer)
    if (len(snparray) / N) + max_cols >= M:
        table_row_expander()

    print "Loaded dataset shape: "
    print dataset.shape
print "Start loading data..."
for i in xrange(0, len(snparray)):
    if i % 1000000 == 0:
        print "Loaded %s so far..." % (i)
    snp = snparray[i]
    pval = pvalarray[i]

    n = snp_hash(snp)
    m = hash_table_indexer[n]
    # Insert inserts a column right before the given indice
    try:
        to_insert = (snp, pval, study)
        dataset[n,m] = to_insert
        hash_table_indexer[n] += 1
    except IndexError:
        print "SHOULD NOT BE HERE!"

print "Done loading the data..."
print "Start saving the data..."
print(time.strftime('%a %H:%M:%S'))

if dset is None:
    f.create_dataset('hash_table', data=dataset, maxshape=(None, M), dtype = dt)
print(time.strftime('%a %H:%M:%S'))
print "Done!"
exit()
