"""
    This is an alternative design to 1a and 2a

    Instead of duplicating the data with C1/B1/SNP1/2D array of studies we have created
    a hash function to store each triple of information (SNPid, p-value, study) in a "bucket"
    (a specific row in the array)

    The bucket/row that each SNP id will be saved into is calculated based on it's SNPid

    Each row may have triples from more than one SNP id but in general the SNP ids should be spread
    relatively evenly across the array

    M, the number of columns of the array, is constant and won't change. It is set to 10.000

    N, is the number of rows/buckets the array will have. If any row is in danger of overflowing, then
    N is doubled (next prime after 2*N) and the snps are re-distributed along the array. Worst case
    scenario, N takes the value of 10 mill - almost the number of unique SNPs in the human genome (I think)
    In this case, each SNP id will belong to each row, and will have the space of 10.000 studies to fill.
    If this happens, if there are more than 10.000 studies for each SNP in the array, we might need to
    think about storing the new data in a different file.
"""

import time
import h5py
import numpy as np
from numpy import genfromtxt
import argparse


class Loader:
    def __init__(self, tsv, h5file, study, snparray=None, pvals=None, chr=None, or_array=None, M=None, N=None):
        self.h5file = h5file
        self.study = study
        # Create my compound type triple to be stored in the hash_table
        self.vlen = h5py.special_dtype(vlen=str)
        self.dt = np.dtype(
            [("snp", self.vlen), ("pval", np.float32), ("chr", np.int), ("or", np.float32), ("study", self.vlen)])

        # the number of columns for each row, should not change
        if M is None:
            self.M = 10000
        else:
            self.M = M
        # the number of rows should double (and go to the next prime) if the columns get full
        if N is None:
            self.N = 4007
        else:
            self.N = N
        # set to true if resize is needed
        self.resize = False

        if tsv is None:
            self.snparray = snparray
            self.pvals = pvals
            self.chr = chr
            self.or_array = or_array
        else:
            print(time.strftime('%a %H:%M:%S'))
            # snp id is a string, so dtype = None
            self.snparray = genfromtxt(tsv, delimiter='\t', usecols=(0), dtype=None)
            self.pvals = genfromtxt(tsv, delimiter='\t', usecols=(1), dtype=float)
            self.chr = genfromtxt(tsv, delimiter='\t', usecols=(2), dtype=int)
            self.or_array = genfromtxt(tsv, delimiter='\t', usecols=(3), dtype=float)
            print "Loaded csv file: ", tsv
            print(time.strftime('%a %H:%M:%S'))

    def load(self):

        f = h5py.File(self.h5file, 'a')

        dataset = f.get("hash_table")

        snparray = self.snparray
        pvalarray = self.pvals
        chrarray = self.chr
        orarray = self.or_array
        study = self.study

        if dataset is None:
            hash_table = create_table_with_empty_elements(self.N, self.M, self.dt)
            # initialize the table indexer to keep the current number of populated columns in each row
            hash_table_indexer = np.zeros((self.N), dtype=int)
            print "Initialized dataset shape:"
            print hash_table.shape
        else:
            hash_table = dataset[:]
            # set current N
            self.N = hash_table.shape[0]
            # for each row in hash_table create the row index that holds the number of columns it has filled
            hash_table_indexer = create_table_row_indexer(hash_table, self.N)
            # if the number of columns is full we need to double the rows of hash_table and recalculate the hashes
            max_cols = max(hash_table_indexer)
            if (len(snparray) / self.N) + max_cols >= self.M:
                hash_table, hash_table_indexer = self.table_row_expander(hash_table)

            print "Loaded dataset shape: "
            print hash_table.shape

        print "Start loading data..."
        for i in xrange(0, len(snparray)):
            if i % 1000000 == 0:
                print "Loaded %s so far..." % (i)
            snp = snparray[i]
            pval = pvalarray[i]
            chr = chrarray[i]
            or_val = orarray[i]

            n = snp_hash(snp, self.N)
            m = hash_table_indexer[n]
            # Insert inserts a column right before the given indice
            try:
                if m + 1 >= self.M:
                    print "expanding mid entry"
                    hash_table, hash_table_indexer = self.table_row_expander(hash_table)
                    n = snp_hash(snp, self.N)
                    m = hash_table_indexer[n]
                hash_table[n][m]["snp"] = snp
                hash_table[n][m]["pval"] = pval
                hash_table[n][m]["chr"] = chr
                hash_table[n][m]["or"] = or_val
                hash_table[n][m]["study"] = study
                hash_table_indexer[n] += 1
            except IndexError:
                print "SHOULD NOT BE HERE!"
                print m
                raise SystemExit(1)

        print "Done loading the data..."
        print "Start saving the data..."
        print(time.strftime('%a %H:%M:%S'))

        if dataset is None:
            f.create_dataset('hash_table', data=hash_table, maxshape=(None, self.M), dtype=self.dt)
        else:
            if self.resize:
                dataset.resize((self.N, self.M))
                dataset[:] = hash_table
                print "resize done"
            else:
                dataset[:] = hash_table
        print(time.strftime('%a %H:%M:%S'))
        print "Done!"

    def table_row_expander(self, hash_table):
        print "Table will soon be out of bounds, expanding rows and re-organizing data starting..."
        # a row is reaching it's capacity of M entries, need to expand rows and re-distribute the snps
        print "N before:", self.N
        self.N = next_N_prime(self.N)
        print "N after:", self.N
        new_hash_table = create_table_with_empty_elements(self.N, self.M, self.dt)
        new_hash_table_indexer = np.zeros((self.N), dtype=int)
        for row in hash_table:
            for element in row:
                snp = element["snp"]
                if snp is "" or snp is None:
                    continue
                n = snp_hash(snp, self.N)
                m = new_hash_table_indexer[n]
                new_hash_table[n][m]["snp"] = snp
                new_hash_table[n][m]["pval"] = element["pval"]
                new_hash_table[n][m]["chr"] = element["chr"]
                new_hash_table[n][m]["or"] = element["or"]
                new_hash_table[n][m]["study"] = element["study"]
                new_hash_table_indexer[n] += 1
        print "done moving the data"
        self.resize = True
        print "doubled the rows in the table and re-organized tha data..."
        return new_hash_table, new_hash_table_indexer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help='The file to be loaded', required=True)
    parser.add_argument('-h5file', help='The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help='The name of the first group this will belong to', required=True)
    args = parser.parse_args()

    tsv = args.tsv
    h5file = args.h5file
    study = args.study

    loader = Loader(tsv, h5file, study)
    loader.load()


def snp_hash(snp, N):
    # p is the first prime after the max number of characters I can get [a-zA-Z0-9] makes 62 unique chars
    p = 67

    # Map A -> 10 ... a -> 36 ... z -> 61
    SNP = [int(c) if c.isdigit() else ord(c) - ord('A') + 10 if c.islower() else ord(c) - ord('A') - 6 + 10 for c in
           snp]

    h = sum(pow(p, i) * c for i, c in enumerate(SNP))

    return h % N  # MODULO


def next_N_prime(n):
    print "calculating next prime"
    primes = [4007, 8017, 16057, 32117, 64237, 128477, 256957, 513917, 10280863]
    idx = primes.index(n)
    if idx == len(primes) - 1:
        print "We do not support growing the table over 10280863 rows"
        print "Consider expanding the primes table or creating a different file"
        exit()
    else:
        return primes[idx + 1]


def create_table_with_empty_elements(n, m, dt):
    emptydt = (None, 0., 0, 0., None)
    table = np.empty((n, m), dtype=dt)
    for i in xrange(n):
        for j in xrange(m):
            table[i][j] = emptydt
    return table


def create_table_row_indexer(table, n):
    hash_table_indexer = np.zeros((n), dtype=int)
    for i in xrange(len(table)):
        hash_table_indexer[i] = len(table[i, :][[table[i, :]["pval"] > 0]])
    return hash_table_indexer


if __name__ == "__main__":
    main()
