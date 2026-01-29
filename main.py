import sys
import json
from io import BytesIO

from models import BSP, VertexLump


def main(bsp_content: bytes):
    bsp_reader = BytesIO(bsp_content)

    bsp = BSP.from_bytes(bsp_reader)

    if not bsp:
        exit()

    vertexlump = VertexLump.from_bytes(BytesIO(bsp.lumps[3].data))

    flat_vertex: list[float] = []
    for v in vertexlump.vertices:
        flat_vertex.append(v.x)
        flat_vertex.append(v.y)
        flat_vertex.append(v.z)

    with open("out.txt", "w") as f:
        f.write(r"\left[" + repr(flat_vertex).replace(" ", "")[1:-1] + r"\right]")

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
