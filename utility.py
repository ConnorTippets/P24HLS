import os, zipfile, io
from os import path


def get_all_with_extension(dir: str, extension: str) -> list[str]:
    prepend = dir
    output = []

    files = os.listdir(dir)
    for file in files:
        path_to_file = path.join(prepend, file)

        if path.isdir(path_to_file):
            output.extend(get_all_with_extension(path_to_file, extension))
        elif path.splitext(file)[1] == extension:
            output.append(path_to_file)

    return output


def get_all_files(dir: str) -> list[str]:
    prepend = dir
    output = []

    files = os.listdir(dir)
    for file in files:
        path_to_file = path.join(prepend, file)

        if path.isdir(path_to_file):
            output.extend(get_all_files(path_to_file))
        else:
            output.append(path_to_file)

    return output


def pakfile_compliant_zip(dir: str, output: str):
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as zip:
        for file in get_all_files(dir):
            print(file)
            zip.write(file, arcname=path.relpath(file, dir).replace("\\", "/"))
