import sys
from io import BytesIO

from models import BSP


def main(bsp_content: bytes):
    bsp_reader = BytesIO(bsp_content)

    print(BSP.from_bytes(bsp_reader))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("i need ts speed")
        exit()

    fname = sys.argv[1]

    with open(fname, "rb") as f:
        contents = f.read()

    main(contents)
