import sys, io
from os import path

from utility import get_all_with_extension
from reader import Reader
from writer import Writer


def convert_all_in_path(dir: str):
    all_vtfs = get_all_with_extension(dir, ".vtf")
    for vtf_path in all_vtfs:
        vtf_out = b""

        with open(vtf_path, "rb") as handle_in:
            with io.BytesIO() as handle_out:
                reader = Reader(handle_in)
                writer = Writer(handle_out)

                skip = reader.read_bytes(4)
                writer.write_bytes(skip)

                major = reader.read_uint()
                minor = reader.read_uint()
                if minor < 5:
                    continue

                print(vtf_path)

                writer.write_uint(7)
                writer.write_uint(4)

                skip = reader.read_bytes()
                writer.write_bytes(skip)

                vtf_out = handle_out.getvalue()

        with open(vtf_path, "wb") as handle:
            handle.write(vtf_out)


def main():
    if len(sys.argv) < 2:
        print("expected usage of tool:")
        print("vtf [dirname]")

        exit(1)

    fname = sys.argv[1]
    convert_all_in_path(fname)


if __name__ == "__main__":
    main()
