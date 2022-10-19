import struct
import gzip
from .pubsub import Publisher, Subscriber
from .file_pointer import FilePointer

ENDIAN = '<'  # only support cpu-type == 2


def unp(fmt, buf):
    r, = struct.unpack(ENDIAN + fmt, buf)
    return r


class GenericOpen:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.fp = None

    def __enter__(self):
        if self.file_path.endswith(".gz"):
            self.fp = gzip.open(self.file_path)
        else:
            self.fp = open(self.file_path, "rb")

        return self.fp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()
