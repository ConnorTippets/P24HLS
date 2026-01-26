import sys
from io import BytesIO

from models import BSP


def main(bsp_content: bytes):
    bsp_reader = BytesIO(bsp_content)

    bsp = BSP.from_bytes(bsp_reader)

    if not bsp:
        exit()

    bsp_output = bsp.to_bytes()

    with open("output.bsp", "wb") as f:
        f.write(bsp_output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("i need ts speed")
        exit()

    fname = sys.argv[1]

    with open(fname, "rb") as f:
        contents = f.read()

    main(contents)
