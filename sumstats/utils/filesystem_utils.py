from os import listdir
from os.path import isfile, join, isdir, basename


def is_valid_dir_path(path, dir_name):
    directory = join(path, dir_name)
    return isdir(directory)


def get_file_path(path, file):
    file_path = join(path, file)
    if not isfile(file_path):
        raise RuntimeError("Something went wrong when trying to get path for file", basename(file_path))
    return file_path


def create_h5file_path(path, dir_name, file_name):
    file_path = join(path, dir_name, "file_" + str(file_name) + ".h5")
    return file_path


def get_h5files_in_dir(path, dir_name):
    # it is up to the filesystem directory to determine what order the files come back in
    # that is why we need to sort them before we return them so the return order is deterministic
    try:
        trait_dir_path = join(path, dir_name)
        return [join(trait_dir_path, f) for f in listdir(trait_dir_path) if isfile(join(trait_dir_path, f))]
    except Exception:
        raise RuntimeError("Something went wrong when trying to get h5files for directory", basename(dir_name))
