import struct, io, typing


class Writer:
    def __init__(self, handle: typing.Union[io.BufferedWriter, io.BytesIO]):
        self.handle = handle

    def _interpret_as(self, raw_data: typing.Any, format: str):
        raw_bytes = struct.pack(format, raw_data)
        self.write_bytes(raw_bytes)

    def position(self) -> int:
        return self.handle.tell()

    def write_bytes(self, raw: bytes):
        self.handle.write(raw)

    def write_bool(self, data: bool):
        self._interpret_as(data, "<?")

    def write_int(self, data: int):
        self._interpret_as(data, "<i")

    def write_uint(self, data: int):
        self._interpret_as(data, "<I")

    def write_ushort(self, data: int):
        self._interpret_as(data, "<H")

    def write_uchar(self, data: int):
        self._interpret_as(data, "<B")

    def write_float(self, data: float):
        self._interpret_as(data, "<f")

    def write_vector(self, data: tuple[float, float, float]):
        x, y, z = data

        self.write_float(x)
        self.write_float(y)
        self.write_float(z)

    def write_qangle(self, data: tuple[float, float, float]):
        self.write_vector(data)

    def write_color32(self, data: tuple[int, int, int, int]):
        r, g, b, a = data

        rgba = a + (b << 8) + (g << 16) + (r << 24)
        self.write_uint(rgba)

    def skip_bytes(self, amount: int):
        self.write_bytes(bytes(amount))
