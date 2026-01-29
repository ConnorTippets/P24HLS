from dataclasses import dataclass
from io import BytesIO
import struct


@dataclass
class Vector:
    x: float
    y: float
    z: float

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "Vector | None":
        data = reader.read(12)
        if not data:
            return

        x, y, z = struct.unpack("<fff", data)
        return cls(x, y, z)


@dataclass
class VertexLump:
    vertices: list[Vector]

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "VertexLump":
        vertices: list[Vector] = []

        while True:
            vector = Vector.from_bytes(reader)
            if not vector:
                break

            vertices.append(vector)

        return cls(vertices)


@dataclass
class Edge:
    a: int
    b: int

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "Edge | None":
        data = reader.read(4)
        if not data:
            return

        a, b = struct.unpack("<HH", data)
        return cls(a, b)


@dataclass
class EdgesLump:
    edges: list[Edge]

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "EdgesLump":
        edges: list[Edge] = []

        while True:
            edge = Edge.from_bytes(reader)
            if not edge:
                break

            edges.append(edge)

        return cls(edges)


@dataclass
class GameLump:
    id: bytes
    offset: int
    version: int
    flags: int
    data: bytes

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "GameLump":
        id: bytes = reader.read(4)
        flags: int = struct.unpack("<H", reader.read(2))[0]
        ver: int = struct.unpack("<H", reader.read(2))[0]
        offset: int = struct.unpack("<i", reader.read(4))[0]
        length: int = struct.unpack("<i", reader.read(4))[0]

        cur_pos = reader.tell()
        reader.seek(offset)
        data = reader.read(length)
        reader.seek(cur_pos)

        return cls(id, offset, ver, flags, data)


@dataclass
class GameLumpHeader:
    lumps: list[GameLump]

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "GameLumpHeader":
        lump_count: int = struct.unpack("<i", reader.read(4))[0]

        lumps: list[GameLump] = []
        for i in range(lump_count):
            lumps.append(GameLump.from_bytes(reader))

        return cls(lumps)

    def to_bytes(self, offset: int) -> bytes:
        packet = struct.pack("<i", len(self.lumps))

        lumps_offset = offset + 4 + 16 * len(self.lumps)
        for lump in self.lumps:
            lump.offset = lumps_offset

            lumps_offset += len(lump.data)

            packet += struct.pack(
                "<bbbbHHii",
                *list(lump.id),
                lump.flags,
                lump.version,
                lump.offset,
                len(lump.data)
            )

        for lump in sorted(self.lumps, key=lambda x: x.offset):
            packet += lump.data

        return packet


@dataclass
class BSPLump:
    id: int
    offset: int
    version: int
    fourcc: tuple[int, int, int, int]
    data: bytes

    @classmethod
    def from_bytes(cls, reader: BytesIO, id: int) -> "BSPLump":
        offset: int = struct.unpack("<i", reader.read(4))[0]
        length: int = struct.unpack("<i", reader.read(4))[0]
        ver: int = struct.unpack("<i", reader.read(4))[0]
        fourcc: tuple[int, int, int, int] = struct.unpack("<BBBB", reader.read(4))

        cur_pos = reader.tell()
        reader.seek(offset)
        data = reader.read(length)
        reader.seek(cur_pos)

        return cls(id, offset, ver, fourcc, data)


@dataclass
class BSP:
    version: int
    map_revision: int
    lumps: list[BSPLump]
    gamelump: GameLumpHeader

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "BSP | None":
        if not reader.read(4) == b"VBSP":
            return

        version: int = struct.unpack("<i", reader.read(4))[0]

        lumps: list[BSPLump] = []
        for i in range(64):
            lumps.append(BSPLump.from_bytes(reader, i))

        map_revision: int = struct.unpack("<i", reader.read(4))[0]

        reader.seek(lumps[35].offset)
        gamelumpheader = GameLumpHeader.from_bytes(reader)

        return cls(version, map_revision, lumps, gamelumpheader)

    def to_bytes(self) -> bytes:
        packet = b"VBSP" + struct.pack("<i", self.version)

        lumps = sorted(self.lumps, key=lambda x: x.id)

        offset = 1036
        for lump in lumps:
            if offset % 4:  # falls outside a 4 byte boundary
                offset += 4 - (offset % 4)  # bring it to the next 4 byte boundary

            packet += struct.pack(
                "<iiiBBBB", offset, len(lump.data), lump.version, *lump.fourcc
            )

            offset += len(lump.data)

        packet += struct.pack("<i", self.map_revision)

        offset = 1036
        for lump in lumps:
            if lump.id == 35:
                lump.data = self.gamelump.to_bytes(offset)

            packet += lump.data

            offset += len(lump.data)

            if offset % 4:  # falls outside a 4 byte boundary
                packet += b"\x00" * (4 - (offset % 4))
                offset += 4 - (offset % 4)  # bring it to the next 4 byte boundary

        return packet
