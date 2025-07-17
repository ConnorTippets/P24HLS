import struct, io, typing

class Writer:
    def __init__(self, handle : typing.Union[io.BufferedWriter, io.BytesIO]):
        self.handle = handle
    
    def _interpret_as(self, raw_data : typing.Any, format : str):
        raw_bytes = struct.pack(format, raw_data)
        self.write_bytes(raw_bytes)
    
    def position(self) -> int:
        return self.handle.tell()
    
    def write_bytes(self, raw : bytes):
        self.handle.write(raw)
    
    def write_int(self, data : int):
        self._interpret_as(data, "<i")
    
    def write_ushort(self, data : int):
        self._interpret_as(data, "<H")
    
    def skip_bytes(self, amount : int):
        self.write_bytes(bytes(amount))