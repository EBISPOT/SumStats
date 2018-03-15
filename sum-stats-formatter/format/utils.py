import gzip
import bz2
import csv

default_cnames = {

    # VARIANT ID
    'SNP': 'VARIANT_ID',
    'MARKERNAME': 'VARIANT_ID',
    'SNPID': 'VARIANT_ID',
    'RS': 'VARIANT_ID',
    'RSID': 'VARIANT_ID',
    'RS_NUMBER': 'VARIANT_ID',
    'RS_NUMBERS': 'VARIANT_ID',
    'ASSAY_NAME': 'VARIANT_ID',
    'ID': 'VARIANT_ID',
    # P-VALUE
    'P': 'P_VALUE',
    'PVALUE': 'P_VALUE',
    'P_VALUE':  'P_VALUE',
    'PVAL': 'P_VALUE',
    'P_VAL': 'P_VALUE',
    'GC_PVALUE': 'P_VALUE',
    'GWAS_P': 'P_VALUE',
    'FREQUENTIST_ADD_PVALUE': 'P_VALUE',
    'SCAN_P': 'P_VALUE',
    'SCANP': 'P_VALUE',
    # CHROMOSOME
    'CHR': 'CHROMOSOME',
    'CHROMOSOME': 'CHROMOSOME',
    'CHROM': 'CHROMOSOME',
    'SCAFFOLD': 'CHROMOSOME',
    # BASE PAIR LOCATION
    'BP': 'BASE_PAIR_LOCATION',
    'POS': 'BASE_PAIR_LOCATION',
    'POSITION': 'BASE_PAIR_LOCATION',
    'PHYS_POS': 'BASE_PAIR_LOCATION',
    # CHROMOSOME COMBINED WITH BASE PAIR LOCATION
    'CHR_POS' : 'CHR_BP',
    'CHRPOS' : 'CHR_BP',
    'CHRPOS_B37' : 'CHR_BP',
    'CHR_POS_B37' : 'CHR_BP',
    'CHRPOS_B36' : 'CHR_BP',
    'CHR_POS_B36' : 'CHR_BP',
    'CHRPOS_B38' : 'CHR_BP',
    'CHR_POS_B38' : 'CHR_BP',
    # ODDS RATIO
    'OR': 'ODDS_RATIO',
    'ODDS_RATIO': 'ODDS_RATIO',
    'ODDSRATIO': 'ODDS_RATIO',
    # OR RANGE
    '95%CI': '95%CI',
    'RANGE': '95%CI',
    # BETA
    'B': 'BETA',
    'BETA': 'BETA',
    'EFFECTS': 'BETA',
    'EFFECT': 'BETA',
    'GWAS_BETA': 'BETA',
    # STANDARD ERROR
    'SE': 'STANDARD_ERROR',
    'STANDARD_ERROR': 'STANDARD_ERROR',
    'STDERR': 'STANDARD_ERROR',
    # EFFECT ALLELE
    'A1': 'EFFECT_ALLELE',
    'ALLELE1': 'EFFECT_ALLELE',
    'ALLELE_1': 'EFFECT_ALLELE',
    'EFFECT_ALLELE': 'EFFECT_ALLELE',
    'REFERENCE_ALLELE': 'EFFECT_ALLELE',
    'REF': 'EFFECT_ALLELE',
    'INC_ALLELE': 'EFFECT_ALLELE',
    'EA': 'EFFECT_ALLELE',
    'ALLELEB': 'EFFECT_ALLELE',
    'ALLELE_B': 'EFFECT_ALLELE',
    # OTHER ALLELE
    'A2': 'OTHER_ALLELE',
    'ALLELE2': 'OTHER_ALLELE',
    'ALLELE_2': 'OTHER_ALLELE',
    'OTHER_ALLELE': 'OTHER_ALLELE',
    'ALT': 'OTHER_ALLELE',
    'NON_EFFECT_ALLELE': 'OTHER_ALLELE',
    'DEC_ALLELE': 'OTHER_ALLELE',
    'NEA': 'OTHER_ALLELE',
    'ALLELEA': 'OTHER_ALLELE',
    'ALLELE_A': 'OTHER_ALLELE',
    # EFFECT ALLELE FREQUENCY
    'EAF': 'EFFECT_ALLELE_FREQUENCY',
    'FRQ': 'EFFECT_ALLELE_FREQUENCY',
    'MAF': 'EFFECT_ALLELE_FREQUENCY',
    'FRQ_U': 'EFFECT_ALLELE_FREQUENCY',
    'F_U': 'EFFECT_ALLELE_FREQUENCY',
    'EFFECT_ALLELE_FREQ': 'EFFECT_ALLELE_FREQUENCY',

    # NUMBER OF STUDIES
    'NSTUDY': 'NSTUDY',
    'N_STUDY': 'NSTUDY',
    'NSTUDIES': 'NSTUDY',
    'N_STUDIES': 'NSTUDY',
    # N
    'N': 'N',
    'NCASE': 'N_CAS',
    'CASES_N': 'N_CAS',
    'N_CASES': 'N_CAS',
    'N_CONTROLS': 'N_CON',
    'N_CAS': 'N_CAS',
    'N_CON': 'N_CON',
    'N_CASE': 'N_CAS',
    'NCONTROL': 'N_CON',
    'CONTROLS_N': 'N_CON',
    'N_CONTROL': 'N_CON',
    'WEIGHT': 'N',  # metal does this. possibly risky.
    # SIGNED STATISTICS
    'ZSCORE': 'Z',
    'Z-SCORE': 'Z',
    'GC_ZSCORE': 'Z',
    'Z': 'Z',
    'LOG_ODDS': 'LOG_ODDS',
    'SIGNED_SUMSTAT': 'SIGNED_SUMSTAT',
    # INFO
    'INFO': 'INFO',
}

CHR_BP = 'CHR_BP'
CHR = 'CHROMOSOME'
BP = 'BASE_PAIR_LOCATION'
VARIANT = 'VARIANT_ID'

VALID_INPUT_HEADERS = set(default_cnames.values())


def get_compression(fh):
    '''
    Read filename suffixes and figure out whether it is gzipped,bzip2'ed or not compressed
    '''
    if fh.endswith('gz'):
        compression = 'gzip'
        openfunc = gzip.open
    elif fh.endswith('bz2'):
        compression = 'bz2'
        openfunc = bz2.BZ2File
    else:
        openfunc = open
        compression = None

    return openfunc, compression


def read_header(fh):
    '''Reads the first line of a file and returns a list with the column names.'''
    (openfunc, compression) = get_compression(fh)
    return set([clean_header(x.rstrip('\n')) for x in openfunc(fh).readline().split()])


def clean_header(header):
    '''
    For cleaning file headers.
    - convert to uppercase
    - replace dashes '-' with underscores '_'
    - replace dots '.' (as in R) with underscores '_'
    - remove newlines ('\n')
    '''
    return header.upper().replace('-', '_').replace('.', '_').replace('\n', '')


def refactor_header(header):
    header = [clean_header(h) for h in header]
    return [default_cnames[h] if h in default_cnames else h for h in header]


def mapped_headers(header):
    return {h: default_cnames[clean_header(h)] for h in header if clean_header(h) in default_cnames}


def get_csv_reader(csv_file):
    dialect = csv.Sniffer().sniff(csv_file.readline())
    csv_file.seek(0)
    return csv.reader(csv_file, dialect)