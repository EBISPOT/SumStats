import argparse
from format.utils import *


def peek(file):
    openfunc, compression = get_compression(file)

    open_file = openfunc(file)
    header = open_file.readline().split()
    row = open_file.readline().split()
    open_file.close()

    for index, h in enumerate(header):
        print(h + " : " + row[index])


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', help='The name of the file to be processed', required=True)
    args = argparser.parse_args()

    file = args.f

    print()
    print("------> Peeking into file:", file, "<------")

    peek(file)


if __name__ == "__main__":
    main()