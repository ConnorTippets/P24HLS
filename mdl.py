import sys, io
from os import path

from utility import get_all_with_extension
from reader import Reader
from writer import Writer


def convert_all_in_path(dir: str):
    all_mdls = get_all_with_extension(dir, ".mdl")
    for mdl_path in all_mdls:
        mdl_out = b""

        with open(mdl_path, "rb") as handle_in:
            with io.BytesIO() as handle_out:
                reader = Reader(handle_in)
                writer = Writer(handle_out)

                skip = reader.read_bytes(4)
                writer.write_bytes(skip)

                ver = reader.read_bytes(1)
                if ver == b"\x00":
                    continue

                print(mdl_path)

                writer.write_bytes(b"\x30")

                skip = reader.read_bytes()
                writer.write_bytes(skip)

                mdl_out = handle_out.getvalue()

        with open(mdl_path, "wb") as handle:
            handle.write(mdl_out)


def main():
    if len(sys.argv) < 2:
        print("expected usage of tool:")
        print("mdl [dirname]")

        exit(1)

    fname = sys.argv[1]
    convert_all_in_path(fname)


if __name__ == "__main__":
    main()
