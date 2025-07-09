import sys

from bsp import BSPReader
from reader import Reader

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("expected usage of tool:")
        print("main [fname].bsp")
    
    fname = sys.argv[1]
    with open(fname, "rb") as handle:
        reader = Reader(handle)
        bsp = BSPReader(reader).read()
    
    print(bsp)