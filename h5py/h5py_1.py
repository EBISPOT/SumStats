"""
    Stores the data in the hierarchy of Trait/Study/DATA
    where DATA:
    under each directory we store 3 (or more) vectors
    snparray will hold the snp ids
    pvals will hold each snps pvalue for this study
    chr will hold each snps position
    or_array will hold each snps odds ratio for this study
    we can add any other information that we want

    the positions in the vectors correspond to each other
    snparray[0], pvals[0], chr[0], and or_array[0] hold the information for SNP 0

"""


import h5py
from numpy import genfromtxt
import argparse


class Loader():

    def __init__(self, csvf, h5file, study, trait, snparray=None, pvals=None, chr=None, or_array=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait

        if csvf is None:
            self.snparray = snparray
            self.pvals = pvals
            self.chr = chr
            self.or_array = or_array
        else:
            # snp id is a string, so dtype = None
            self.snparray = genfromtxt(csvf, delimiter = '\t', usecols = (0), dtype = None)
            self.pvals = genfromtxt(csvf, delimiter = '\t', usecols = (1), dtype = float)
            self.chr = genfromtxt(csvf, delimiter = '\t', usecols = (2), dtype = int)
            self.or_array = genfromtxt(csvf, delimiter = '\t', usecols = (3), dtype = float)

    def load(self):

        h5file = self.h5file
        study = self.study
        trait = self.trait

        # snp id is a string, so dtype = None
        snparray = self.snparray
        pvals = self.pvals
        chr = self.chr
        or_array = self.or_array

        # Open the file with read/write permissions and create if it doesn't exist
        f = h5py.File(h5file, 'a')

        if trait in f:
            trait_group = f[trait]
            if study in trait_group:
                study_group = trait_group[study]
            else:
                study_group = trait_group.create_group(study)
        else:
            study_group = f.create_group(trait + "/" + study)


        study_group.create_dataset('snps', data=snparray)
        study_group.create_dataset('pvals', data=pvals)
        study_group.create_dataset('chr', data=chr)
        study_group.create_dataset('or', data=or_array)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help = 'The file to be loaded')
    parser.add_argument('-h5file', help = 'The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help = 'The name of the first group this will belong to', required=True)
    parser.add_argument('-trait', help = 'The name of the trait the SNPs of this file are related to', required=True)
    args = parser.parse_args()

    csvf = args.CSV_input_file
    h5file = args.HDF5_output_file
    study = args.study_name
    trait = args.trait_name

    loader = Loader(csvf, h5file, study, trait)
    loader.load()

if __name__ == '__main__':
    main()