from reader import Reader
from writer import Writer


class WorldLightConverter:
    def __init__(self, reader: Reader, writer: Writer):
        self.reader = reader
        self.writer = writer

    def convert(self):
        while True:
            skip = self.reader.read_bytes(40)
            if len(skip) < 40:
                break
            self.writer.write_bytes(skip)

            type = self.reader.read_uint()
            style = self.reader.read_int()

            print(f"Type: {type}\nStyle: {style}")

            self.writer.write_uint(3)
            self.writer.write_bytes(b"\x00\xff\xff\xff")

            skip = self.reader.read_bytes(40)
            if len(skip) < 40:
                break
            self.writer.write_bytes(skip)
