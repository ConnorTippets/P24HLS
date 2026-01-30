import sys
import json
from io import BytesIO

from models import BSP, VertexLump, EdgesLump, SurfedgesLump


def main(bsp_content: bytes):
    bsp_reader = BytesIO(bsp_content)

    bsp = BSP.from_bytes(bsp_reader)

    if not bsp:
        exit()

    vertexlump = VertexLump.from_bytes(BytesIO(bsp.lumps[3].data))
    edgeslump = EdgesLump.from_bytes(BytesIO(bsp.lumps[12].data))
    surfedgeslump = SurfedgesLump.from_bytes(BytesIO(bsp.lumps[13].data))

    for v in vertexlump.vertices:
        print(f"v {v.x} {v.y} {v.z}")

    print()

    for e in edgeslump.edges:
        print(f"l {e.a+1} {e.b+1}")

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
