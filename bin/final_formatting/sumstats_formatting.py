from utils import *
import csv
import argparse
from format import peek


def add_blank_col_to_row(row, headers_to_add):
    for h in headers_to_add:
        row.append('None')
    return row

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', required=True)
    args = argparser.parse_args()

    file = args.f
    filename = get_filename(file)
    what_changed = None
    new_header = None
    is_header = True
    headers_to_add = []
    lines = []

    with open(file) as csv_file:
        csv_reader = get_csv_reader(csv_file)

        for row in csv_reader:
            if is_header:
                what_changed = mapped_headers(row[:])
                new_header = refactor_header(row)
                headers_to_add = missing_headers(new_header)
                new_header.extend(headers_to_add)
                is_header = False
            else:
                row = add_blank_col_to_row(row, headers_to_add)
                lines.append(row)
        

    new_filename = 'sumstats_' + filename + '.tsv'
    with open(new_filename, 'w') as result_file:
        writer = csv.writer(result_file, delimiter='\t')
        writer.writerows([new_header])
        writer.writerows(lines)

    print("\n")
    print("------> Output saved in file:", new_filename, "<------")
    print("\n")
    print("Showing how the headers where mapped below...")
    print("\n")
    for key, value in what_changed.items():
        print(key, " -> ", value)
    print("\n")
    if headers_to_add:
        print("The following headers were missing, and have been added with 'NA' values:")
        print("\n")
        for h in headers_to_add:
            print(h)
    else:
        print("All required headers were found in input file.")
    print("\n")
    print("Peeking into the new file...")
    print("\n")
    peek.peek(new_filename)


if __name__ == "__main__":
    main()
