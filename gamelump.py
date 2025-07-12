from dataclasses import dataclass

from reader import Reader
from writer import Writer

@dataclass
class GameLumpHeader:
    id : bytes
    flags : int
    version : int
    offset : int
    length : int
    
@dataclass
class GameLump:
    data : bytes

@dataclass
class GameLumps:
    gamelumps : list[GameLump]
    gamelump_headers : list[GameLumpHeader]

class GameLumpReader:
    def __init__(self, gamelump_offset : int, reader : Reader):
        self.gamelump_offset = gamelump_offset
        self.reader = reader
    
    def read_header(self) -> list[GameLumpHeader]:
        gamelump_count = self.reader.read_int()
        gamelump_headers = []
        
        for _ in range(gamelump_count):
            id = self.reader.read_bytes(4)
            flags = self.reader.read_ushort()
            version = self.reader.read_ushort()
            offset = self.reader.read_int()
            length = self.reader.read_int()
            
            gamelump_headers.append(GameLumpHeader(id, flags, version, offset, length))
        
        return gamelump_headers
    
    def read(self) -> GameLumps:
        gamelump_headers = self.read_header()
        gamelumps = []
        
        for header in gamelump_headers:
            self.reader.go_to(header.offset - self.gamelump_offset)
            gamelump_data = self.reader.read_bytes(header.length)
            
            gamelumps.append(GameLump(gamelump_data))
        
        return GameLumps(gamelumps, gamelump_headers)

class GameLumpWriter:
    def __init__(self, gamelump_offset : int, writer : Writer):
        self.gamelump_offset = gamelump_offset
        self.writer = writer
    
    def write_header(self, gamelump : GameLumps):
        gamelump_count = len(gamelump.gamelumps)
        
        self.writer.write_int(gamelump_count)
        
        offset = 4 + (gamelump_count * 16) + self.gamelump_offset
        for i, header in enumerate(gamelump.gamelump_headers):
            lump = gamelump.gamelumps[i]
            
            self.writer.write_bytes(header.id)
            self.writer.write_ushort(header.flags)
            self.writer.write_ushort(header.version)
            self.writer.write_int(offset)
            self.writer.write_int(len(lump.data))
            
            offset += len(lump.data)
    
    def write(self, gamelump : GameLumps):
        self.write_header(gamelump)
        
        for lump in gamelump.gamelumps:
            self.writer.write_bytes(lump.data)

class GameLumpConverter:
    def __init__(self, gamelump_offset : int, new_gamelump_offset : int, reader : Reader, writer : Writer):
        self.reader = GameLumpReader(gamelump_offset, reader)
        self.writer = GameLumpWriter(new_gamelump_offset, writer)
    
    def convert(self):
        gamelump = self.reader.read()
        self.writer.write(gamelump)