import csv
import pandas as pd
from typing import List, Dict, Tuple
import os


class IedaRow:
    def __init__(self, d: dict):
        self.x = int(d["x"])
        self.y = int(d["y"])
        self.site = int(d["site"])
        self.sb = int(d["sb"])
        self.hb = int(d["hb"])

    @property
    def key(self) -> Tuple[int, int]:
        return self.x, self.y


class Ieda:
    def __init__(self, file_path: str):
        self._file_path = file_path
        self.rows: List[IedaRow] = []
        self.result: Dict[Tuple[int, int], IedaRow] = {}

        with open(file_path, "r") as f_in:
            reader = csv.DictReader(f_in)
            for d in reader:
                iedaRow = IedaRow(d)
                self.rows.append(iedaRow)
                self.result[iedaRow.key] = iedaRow

    def get_ieda_row(self, key: Tuple[int, int]) -> IedaRow:
        return self.result.get(key, None)

    def get_sb(self, key: Tuple[int, int]) -> int:
        row = self.result.get(key, None)
        if row is None:
            return -1
        return row.sb


def get_good_die_count_list(ieda: Ieda) -> List[int]:
    res = []
    for _, df_row in df.iterrows():
        site1_x, site1_y = df_row['x'], df_row['y']
        res.append(get_good_die_count(ieda, site1_x, site1_y))
    return res


def get_good_die_count(ieda: Ieda, site1_x: int, site1_y: int) -> int:
    good_die_count = 0
    for offset_x, offset_y in [(0, 0), (0, 2), (0, 4), (0, 6), (0, 8), (0, 10), (0, 12), (0, 14)]:
        xx, yy = site1_x + offset_x, site1_y + offset_y
        row = ieda.get_ieda_row((xx, yy))
        if row is None:
            continue
        good_die_count += (row.hb == 1)
    return good_die_count


if __name__ == '__main__':
    site0_xy_csv = r"C:\log\w235_char_wafer_map_sampling\PS-R610ISM8-9--40-12AENG.CSV"
    df = pd.read_csv(site0_xy_csv)

    working_dir = r"C:\log\w235_char_wafer_map_sampling\ieda"
    for cur_dir, dirs, file_names in os.walk(working_dir):
        for file_name in file_names:
            if not file_name.endswith(".csv"):
                continue
            good_list = get_good_die_count_list(Ieda(os.path.join(cur_dir, file_name)))
            df[file_name.replace(".csv", "")] = good_list
    df.to_csv(r"C:\log\w235_char_wafer_map_sampling\export2.csv")
