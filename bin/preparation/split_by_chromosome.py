import csv
import argparse
import os


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The full path to the file to be processed', required=True)
    argparser.add_argument('-path', help='The path to the directory where the files will be stored', required=True)
    argparser.add_argument('-chr', help='Chromosome whose data we are going to extract', required=True)
    args = argparser.parse_args()

    file = args.f
    path = args.path
    chromosome = int(args.chr)
    filename = file.split("/")[-1].split(".")[0]

    chromosome_index = None
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
                chromosome_index = header.index('chromosome')
                is_header = False
            else:
                if int(row[chromosome_index]) == chromosome:
                    lines.append(row)

    if len(lines) > 0:
        new_filename = os.path.join(path, 'chr_' + str(chromosome) + "_" + filename + '.tsv')
        with open(new_filename, 'w') as result_file:
            writer = csv.writer(result_file, delimiter='\t')
            writer.writerows([header])
            writer.writerows(lines)


if __name__ == "__main__":
    main()