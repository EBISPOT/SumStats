import argparse
import numpy as np

def argument_checker():
    args = argument_parser(**locals())

    if args.query == "1":
        if args.trait is None:
            print "Query 1 -- Retrieve all information for a specific trait -- "
            print "input: query number (1) and trait name"
            exit(1)
    elif args.query == "2":
        if args.study is None or args.trait is None:
            print "Query 2 -- Retrieve all the information for a specific study --"
            print "input: query number (2), study name and trait name"
            exit(1)
    elif args.query == "3":
        if args.snp is None:
            print "Query 3 -- Retrieve all information for a single SNP -- "
            print "input: query number (3) and snp id"
            exit(1)
    elif args.query == "4":
        if args.chr is None:
            print "Query 4 -- Retrieve all information for SNPs that belong to a chromosome -- "
            print "input: query number (4) and chromosome"
            exit(1)
    elif args.query == "5":
        if args.trait is None or args.snp is None:
            print "Query 5 -- Retrieve all information for a trait and a single SNP -- "
            print "input: query number (5), trait and snp id"
            exit(1)
    elif args.query == "6":
        if args.trait is None or args.chr is None:
            print "Query 6 -- Retrieve all information for SNPs that belong to a chromosome and a specific trait -- "
            print "input: query number (6), chromosome and trait"
            exit(1)
    else:
        print "Wrong input"
        exit(1)


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-h5file', help='The name of the HDF5 file', required=True)
    parser.add_argument('-query', help='The nmber of the query to perform', required=True)
    parser.add_argument('-study', help='The study I am looking for')
    parser.add_argument('-trait', help='The trait I am looking for')
    parser.add_argument('-snp', help='The SNP I am looking for')
    parser.add_argument('-chr', help='The chromosome whose SNPs I want')
    parser.add_argument('-pu', help='The upper limit for the p-value')
    parser.add_argument('-pl', help='The lower limit for the p-value')

    return parser.parse_args()
