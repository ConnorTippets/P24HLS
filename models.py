from dataclasses import dataclass
from io import BytesIO
import struct


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

    @classmethod
    def from_bytes(cls, reader: BytesIO) -> "BSP | None":
        if not reader.read(4) == b"VBSP":
            return

        version: int = struct.unpack("<i", reader.read(4))[0]

        lumps: list[BSPLump] = []
        for i in range(64):
            lumps.append(BSPLump.from_bytes(reader, i))

        map_revision: int = struct.unpack("<i", reader.read(4))[0]

        return cls(version, map_revision, lumps)

    def to_bytes(self) -> bytes:
        header = b"VBSP" + struct.pack("<i", self.version)
        lumps_out = bytes()

        header_lumps = sorted(self.lumps, key=lambda x: x.id)

        in_lumps = sorted(self.lumps, key=lambda x: x.offset)

        offset_offset = 0
        for lump in header_lumps:
            offset = lump.offset + offset_offset

            if offset % 4:  # falls outside a 4 byte boundary
                offset_offset += 4 - (
                    offset_offset % 4
                )  # bring it to the next 4 byte boundary

            offset = lump.offset + offset_offset

            header += struct.pack(
                "<iiiBBBB", offset, len(lump.data), lump.version, *lump.fourcc
            )

        offset = 1036
        for lump in in_lumps:
            lumps_out += lump.data

            offset += len(lump.data)

            if offset % 4:  # falls outside a 4 byte boundary
                lumps_out += b"\x00" * (4 - (offset % 4))
                offset += 4 - (offset % 4)  # bring it to the next 4 byte boundary

        header += struct.pack("<i", self.map_revision)

        return header + lumps_out
