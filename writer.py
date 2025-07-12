import struct, io

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
    
    def write_ushort(self, data : int):
        raw_data = struct.pack("<H", data)
        self.write_bytes(raw_data)
    
    def skip_bytes(self, amount : int):
        self.write_bytes(bytes(amount))