import os
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
