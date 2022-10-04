import gzip


class FilePointer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.fp: any = None

    def __enter__(self):
        if self.file_path.endswith(".gz"):
            self.fp = gzip.open(self.file_path)
        else:
            self.fp = open(self.file_path, "rb")
        return self.fp

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()
