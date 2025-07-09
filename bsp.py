from dataclasses import dataclass

from reader import Reader

HEADER_LUMPS = 64

@dataclass
class LumpHeader:
    offset:  int
    length:  int
    version: int
    fourCCs: int

@dataclass
class BSPHeader:
    version: int
    lump_headers: list[LumpHeader]
    map_revision: int

@dataclass
class Lump:
    version: int
    data: bytes

@dataclass
class BSP:
    def __repr__(self):
        return f"BSP\nVersion: {self.version}\nMap Revision: {self.map_revision}"

    version: int
    lumps: list[Lump]
    map_revision: int

class BSPReader:
    def __init__(self, reader : Reader):
        self.reader = reader
    
    def read_header(self) -> BSPHeader:
        magic_num = self.reader.read_bytes(4)
        if not magic_num == b"VBSP":
            raise Exception("input BSP is invalid!")
        
        version = self.reader.read_int()
        
        lump_headers = []
        for _ in range(HEADER_LUMPS):
            lump_offset  = self.reader.read_int()
            lump_length  = self.reader.read_int()
            lump_version = self.reader.read_int()
            lump_fourCCs = self.reader.read_int()
            
            lump_headers.append(LumpHeader(lump_offset, lump_length, lump_version, lump_fourCCs))
        
        map_revision = self.reader.read_int()
        
        return BSPHeader(version, lump_headers, map_revision)
    
    def read_lumps(self, lump_headers) -> list[Lump]:
        lumps = []
        for i in range(HEADER_LUMPS):
            lump_header = lump_headers[i]
            
            self.reader.go_to(lump_header.offset)
            lump_data = self.reader.read_bytes(lump_header.length)
            
            lumps.append(Lump(lump_header.version, lump_data))
        
        return lumps
    
    def read(self) -> BSP:
        header = self.read_header()
        lumps = self.read_lumps(header.lump_headers)
        
        return BSP(header.version, lumps, header.map_revision)

#class BSPWriter