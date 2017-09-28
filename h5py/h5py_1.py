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
import time


class Loader():

    def __init__(self, tsv, h5file, study, trait, snp_array=None, pval_array=None, chr_array=None, or_array=None,
                 bp_array=None, effect_array=None, other_array=None):
        self.h5file = h5file
        self.study = study
        self.trait = trait

        if tsv is None:
            loaded = False
            if snp_array is not None and pval_array is not None and chr_array is not None and or_array is not None and bp_array is not None and effect_array is not None and other_array is not None:
                if len(snp_array) != 0 and len(pval_array) != 0 and len(chr_array) != 0 and len(or_array) != 0 and len(bp_array) != 0 and len(effect_array) != 0 and len(other_array) != 0:
                    loaded = True
                    self.snp_array = snp_array
                    self.pval_array = pval_array
                    self.chr_array = chr_array
                    self.or_array = or_array
                    self.bp_array = bp_array
                    self.effect_array = effect_array
                    self.other_array = other_array
            if not loaded:
                print "If no tsv file provided, the arrays containing the study info must not be empty or None"
                raise SystemExit(1)
        else:
            # trait = args.trait_name
            print(time.strftime('%a %H:%M:%S'))

            # snp id is a string, so dtype = None
            # will be ndarrays
            self.snp_array = genfromtxt(tsv, delimiter='\t', usecols=(0), dtype=None)
            self.pval_array = genfromtxt(tsv, delimiter='\t', usecols=(1), dtype=float)
            self.chr_array = genfromtxt(tsv, delimiter='\t', usecols=(2), dtype=int)
            self.or_array = genfromtxt(tsv, delimiter='\t', usecols=(3), dtype=float)
            self.bp_array = genfromtxt(tsv, delimiter='\t', usecols=(4), dtype=int)
            self.effect_array = genfromtxt(tsv, delimiter='\t', usecols=(5), dtype=None)
            self.other_array = genfromtxt(tsv, delimiter='\t', usecols=(6), dtype=None)

            print "Loaded tsv file: ", tsv
            print(time.strftime('%a %H:%M:%S'))

    def load(self):

        h5file = self.h5file
        study = self.study
        trait = self.trait

        # snp id is a string, so dtype = None
        snp_array = self.snp_array
        pval_array = self.pval_array
        chr_array = self.chr_array
        or_array = self.or_array
        bp_array = self.bp_array
        effect_array = self.effect_array
        other_array = self.other_array

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

        study_group.create_dataset('snp', data=snp_array)
        study_group.create_dataset('pval', data=pval_array)
        study_group.create_dataset('chr', data=chr_array)
        study_group.create_dataset('or', data=or_array)

        study_group.create_dataset('bp', data=bp_array)
        study_group.create_dataset('effect', data=effect_array)
        study_group.create_dataset('other', data=other_array)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-tsv', help = 'The file to be loaded')
    parser.add_argument('-h5file', help = 'The name of the HDF5 file to be created/updated', required=True)
    parser.add_argument('-study', help = 'The name of the first group this will belong to', required=True)
    parser.add_argument('-trait', help = 'The name of the trait the SNPs of this file are related to', required=True)
    args = parser.parse_args()

    tsv = args.tsv
    h5file = args.h5file
    study = args.study
    trait = args.trait

    loader = Loader(tsv, h5file, study, trait)
    loader.load()

if __name__ == '__main__':
    main()