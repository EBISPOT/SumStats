import pandas as pd
import argparse
import os
import sumstats.utils.sqlite_client as sq 


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-vcf', help='The name of the vcf to be processed', required=True)
    argparser.add_argument('-db', help='The name of the database to load to', required=True)
    args = argparser.parse_args()
    db = args.db
    vcf = args.vcf

    vcfdf = pd.read_csv(vcf, sep='\t', 
                        comment='#', 
                        header=None, 
                        dtype=str, 
                        usecols=[0, 1, 2], 
                        names=['CHROM', 'POS', 'RSID']
                        )
        
    vcfdf.RSID = vcfdf.RSID.str.replace("rs","")
    vcfdf.CHROM =vcfdf.CHROM.replace({'X': 23, 'Y': 24, 'MT': 25})

    sql = sq.sqlClient(db)
    sql.drop_rsid_index()
    list_of_tuples = list(vcfdf.itertuples(index=False, name=None))
    sql.cur.execute('BEGIN TRANSACTION')
    sql.cur.executemany("insert or ignore into snp(chr, position, rsid) values (?, ?, ?)", list_of_tuples)
    sql.cur.execute('COMMIT')
    sql.create_rsid_index()



if __name__ == '__main__':
    main()
