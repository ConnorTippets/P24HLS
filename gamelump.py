from dataclasses import dataclass, astuple
import io

from constants import STATICPROPSGAMELUMP_ID
from prpsgamelump import StaticPropsGameLumpConverter
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
    def find_from_id(self, id : bytes) -> GameLump:
        for i, header in enumerate(self.gamelump_headers):
            if header.id == id:
                return self.gamelumps[i]
        
        raise Exception(f"unable to find gamelump with id {repr(id)}")
    
    def find_header_from_id(self, id : bytes) -> GameLumpHeader:
        for header in self.gamelump_headers:
            if header.id == id:
                return header
        
        raise Exception(f"unable to find gamelump with id {repr(id)}")
    
    def set_lump_from_id(self, id : bytes, gamelump : GameLump, gamelump_header : GameLumpHeader):
        lump_index = 0
        
        for i, header in enumerate(self.gamelump_headers):
            if header.id == id:
                lump_index = i
        
        self.gamelumps[lump_index] = gamelump
        self.gamelump_headers[lump_index] = gamelump_header
    
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
    def __init__(self, gamelump_offset : int, new_gamelump_offset : int, new_prps_version : int, reader : Reader, writer : Writer):
        self.new_prps_version = new_prps_version
        self.reader = GameLumpReader(gamelump_offset, reader)
        self.writer = GameLumpWriter(new_gamelump_offset, writer)
    
    def convert(self):
        gamelump = self.reader.read()
        
        staticgamelump_data = gamelump.find_from_id(STATICPROPSGAMELUMP_ID).data
        _, staticgamelump_flags, staticgamelump_version, _, _ = astuple(gamelump.find_header_from_id(STATICPROPSGAMELUMP_ID))
        staticgamelump_out = b''
        
        with io.BytesIO(staticgamelump_data) as handle_in:
            with io.BytesIO() as handle_out:
                reader = Reader(handle_in)
                writer = Writer(handle_out)
                StaticPropsGameLumpConverter(reader, writer, staticgamelump_version, self.new_prps_version).convert()
                
                staticgamelump_out = handle_out.getvalue()
        
        gamelump.set_lump_from_id(STATICPROPSGAMELUMP_ID, GameLump(staticgamelump_out), GameLumpHeader(STATICPROPSGAMELUMP_ID, staticgamelump_flags, self.new_prps_version, 0, 0))
        
        self.writer.write(gamelump)