from reader import Reader
from writer import Writer


class BrushSideConverter:
    def __init__(self, reader: Reader, writer: Writer):
        self.reader = reader
        self.writer = writer

    def convert(self):
        while True:
            skip = self.reader.read_bytes(7)
            if len(skip) < 7:
                break
            self.writer.write_bytes(skip)
            self.writer.write_bytes(b"\x00")
            self.reader.skip_bytes(1)
