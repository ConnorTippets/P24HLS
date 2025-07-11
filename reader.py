import struct, io, os

class Reader:
    def __init__(self, handle : io.BufferedReader):
        self.handle = handle
    
    def position(self) -> int:
        return self.handle.tell()
    
    def go_to(self, offset : int):
        self.handle.seek(offset)
    
    def read_bytes(self, amount : int) -> bytes:
        return self.handle.read(amount)
    
    def read_int(self) -> int:
        raw_data = self.read_bytes(4)
        return struct.unpack("<i", raw_data)[0]
    
    def skip_bytes(self, amount : int):
        self.handle.seek(amount, os.SEEK_CUR)

class Writer:
    def __init__(self, handle : io.BufferedWriter):
        self.handle = handle
    
    def position(self) -> int:
        return self.handle.tell()
    
    def write_bytes(self, raw : bytes):
        self.handle.write(raw)
    
    def write_int(self, data : int):
        raw_data = struct.pack("<i", data)
        self.write_bytes(raw_data)
    
    def skip_bytes(self, amount : int):
        self.write_bytes(bytes(amount))