import struct

class Reader:
    def __init__(self, handle):
        self.handle = handle
    
    def go_to(self, offset):
        self.handle.seek(offset)
    
    def read_bytes(self, amount) -> bytes:
        return self.handle.read(amount)
    
    def read_int(self) -> int:
        raw_data = self.read_bytes(4)
        return struct.unpack("<i", raw_data)[0]