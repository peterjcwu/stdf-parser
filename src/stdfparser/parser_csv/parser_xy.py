import os
import csv
from parser_base import ParserBase


class PRRData:
    def __init__(self, d: dict):
        self.x: int = d["X_COORD"]
        self.y: int = d["Y_COORD"]
        self.site: int = d["SITE_NUM"]
        self.hb: int = d["HARD_BIN"]
        self.sb: int = d["SOFT_BIN"]

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "site": self.site,
            "hb": self.hb,
            "sb": self.sb,
        }


def prr_handler(parser):
    prr = PRRData(parser.data)
    parser.rows.append(prr)


class ParserXY(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)
        self.handlers = {
            "Prr": prr_handler,
        }
        self.rows = []

    def take(self, typ_sub):
        record = self.Rec_Dict.get(typ_sub)
        if record is None or record.name not in self.handlers:
            return
        handler = self.handlers.get(record.name)
        handler(self)

    @property
    def export_path(self):
        return self.file_path.replace(".stdf.gz", ".csv")

    def export(self):
        with open(self.export_path, "w", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=["x", "y", "site", 'hb', 'sb'])
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row.to_dict())

def rr():
    pass


def loop_func(working_dir: str, filter_func, workload_func):
    for cur_dir, dirs, file_names in os.walk(working_dir):
        for file_name in file_names:
            if filter_func is not None and filter_func(file_name):
                continue
            workload_func(os.path.join(cur_dir, file_name))


def export_xy(file_path: str) -> None:
    ParserXY().parse(file_path).export()


if __name__ == '__main__':
    export_xy(r"C:\Users\nxf79056\Downloads\KY20W_SWSB37BD3000_KY20W12-D2_20220914125156.stdf.gz")
