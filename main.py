import sys

from bsp import BSPReader, BSPWriter
from reader import Reader, Writer

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("expected usage of tool:")
        print("main [fname].bsp")
    
    fname = sys.argv[1]
    with open(fname, "rb") as handle:
        reader = Reader(handle)
        bsp = BSPReader(reader).read()
    
    with open(fname[:-4] + "_d.bsp", "wb") as handle:
        writer = Writer(handle)
        BSPWriter(writer).write(bsp)