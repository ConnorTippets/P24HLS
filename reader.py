import struct, io, os, typing

class Reader:
    def __init__(self, handle : typing.Union[io.BufferedReader, io.BytesIO]):
        self.handle = handle
    
    def _interpret_as(self, amount : int, format):
        raw_data = self.read_bytes(amount)
        return struct.unpack(format, raw_data)[0]
    
    def position(self) -> int:
        return self.handle.tell()
    
    def go_to(self, offset : int):
        self.handle.seek(offset)
    
    def read_bytes(self, amount : int) -> bytes:
        return self.handle.read(amount)
    
    def read_int(self) -> int:
        return self._interpret_as(4, "<i")
    
    def read_ushort(self) -> int:
        return self._interpret_as(2, "<H")
    
    def read_uchar(self) -> int:
        return self._interpret_as(2, "<B")
    
    def read_float(self) -> float:
        return self._interpret_as(4, "<f")
    
    def read_vector(self) -> tuple[float, float, float]:
        x = self.read_float()
        y = self.read_float()
        z = self.read_float()
        return x, y, z
    
    def read_qangle(self) -> tuple[float, float, float]:
        return self.read_vector()
    
    def skip_bytes(self, amount : int):
        self.handle.seek(amount, os.SEEK_CUR)
