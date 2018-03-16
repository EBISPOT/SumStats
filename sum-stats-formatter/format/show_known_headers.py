from format.utils import *


def main():
    print()
    print("Showing known valid column headers...")
    print()
    for header in VALID_INPUT_HEADERS:
        print(header)
    print()
    print("Showing desired headers...")
    print()
    for header in DESIRED_HEADERS:
        print(header)
    print()


if __name__ == "__main__":
    main()