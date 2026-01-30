import sys
import json
from io import BytesIO

from models import BSP, VertexLump, EdgesLump, SurfedgesLump, FacesLump, Edge


def main(bsp_content: bytes):
    bsp_reader = BytesIO(bsp_content)

    bsp = BSP.from_bytes(bsp_reader)

    if not bsp:
        exit()

    vertexlump = VertexLump.from_bytes(BytesIO(bsp.lumps[3].data))
    edgeslump = EdgesLump.from_bytes(BytesIO(bsp.lumps[12].data))
    surfedgeslump = SurfedgesLump.from_bytes(BytesIO(bsp.lumps[13].data))
    faceslump = FacesLump.from_bytes(BytesIO(bsp.lumps[7].data))

    edgesperface: list[list[list[int]]] = []
    for face in faceslump.faces:
        surfedges = surfedgeslump.surfedges[
            face.firstedge : face.firstedge + face.numedges
        ]

        edges: list[list[int]] = []
        for surfedge in surfedges:
            edge = edgeslump.edges[abs(surfedge)]
            a, b = edge.a, edge.b

            if surfedge < 0:
                a, b = b, a

            edges.append([a, b])
        edgesperface.append(edges)

    triangles: list[list[int]] = []
    for edges in edgesperface:
        vertices = [edge[0] for edge in edges]

        for i in range(2, len(vertices)):
            triangles.append([vertices[0], vertices[i - 1], vertices[i]])

    for v in vertexlump.vertices:
        print(f"v {v.x} {v.z} {v.y}")

    print()

    for tri in triangles:
        print(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}")

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
