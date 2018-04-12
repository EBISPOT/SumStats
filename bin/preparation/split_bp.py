import argparse
import csv
import os


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The full path to the file to be processed', required=True)
    argparser.add_argument('-path', help='The path to the directory where the files will be stored', required=True)
    argparser.add_argument('-start', help='Start of base pair location', required=True)
    argparser.add_argument('-end', help='End of base pair location', required=True)
    argparser.add_argument('-accession', help='Accession number of bp in the chromosome scheme', required=True)
    args = argparser.parse_args()

    file = args.f
    start = float(args.start)
    end = float(args.end)
    accession = args.accession
    path = args.path

    filename = file.split("/")[-1].split(".")[0]
    bp_index = None
    header = None
    is_header = True

    lines = []
    with open(file) as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.readline())
        csv_file.seek(0)
        csv_reader = csv.reader(csv_file, dialect)
        for row in csv_reader:
            if is_header:
                header = row
                bp_index = header.index('base_pair_location')
                is_header = False
            else:
                if start <= int(row[bp_index]) < end:
                    lines.append(row)

    if len(lines) > 0:
        new_filename = os.path.join(path, 'bp_' + accession + "_" + filename + '.tsv')
        with open(new_filename, 'w') as result_file:
            writer = csv.writer(result_file, delimiter='\t')
            writer.writerows([header])
            writer.writerows(lines)


if __name__ == "__main__":
    main()
