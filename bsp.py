from dataclasses import dataclass

from reader import Reader
from writer import Writer
from constants import HEADER_LUMPS, IDENT

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
    def set_lump(self, id : int, lump : Lump, header : LumpHeader):
        self.lumps[id] = lump
        self.header.lump_headers[id] = header
    
    def __repr__(self):
        return f"BSP\nVersion: {self.version}\nMap Revision: {self.map_revision}"

    version: int
    header: BSPHeader
    lumps: list[Lump]
    map_revision: int

def calc_new_offset(bsp : BSP, id : int):
    if len(bsp.lumps[id].data) == 0:
        return 0
    
    offset = 1036
    for i in range(id):
        offset += len(bsp.lumps[i].data)

        if offset % 4:
            offset += (4 - offset % 4)
    
    return offset

class BSPReader:
    def __init__(self, reader : Reader):
        self.reader = reader
    
    def read_header(self) -> BSPHeader:
        magic_num = self.reader.read_bytes(4)
        if not magic_num == IDENT:
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
            lump_header : LumpHeader = lump_headers[i]
            
            self.reader.go_to(lump_header.offset)
            lump_data = self.reader.read_bytes(lump_header.length)
            
            lumps.append(Lump(lump_header.version, lump_data))
        
        return lumps
    
    def read(self) -> BSP:
        header = self.read_header()
        lumps = self.read_lumps(header.lump_headers)
        
        return BSP(header.version, header, lumps, header.map_revision)

class BSPWriter:
    def __init__(self, writer : Writer):
        self.writer = writer
    
    def write_header(self, bsp : BSP):
        self.writer.write_bytes(b'VBSP')
        self.writer.write_int(bsp.version)
        
        offset = 1036
        for i in range(HEADER_LUMPS):
            lump : Lump = bsp.lumps[i]
            length = len(lump.data)
            
            if length == 0:
                self.writer.write_int(0)
                self.writer.write_int(0)
                self.writer.write_int(0)
                self.writer.write_int(0)
            else:
                self.writer.write_int(offset)
                self.writer.write_int(length)
                self.writer.write_int(lump.version)
                self.writer.write_int(0)
            
            offset += length
            if offset % 4:
                offset += (4 - (offset % 4))
        
        self.writer.write_int(bsp.map_revision)
    
    def write_lumps(self, lumps: list[Lump]):
        for lump in lumps:
            self.writer.write_bytes(lump.data)
            
            if self.writer.position() % 4:
                self.writer.skip_bytes(4 - (self.writer.position() % 4))
    
    def write(self, bsp : BSP):
        self.write_header(bsp)
        self.write_lumps(bsp.lumps)