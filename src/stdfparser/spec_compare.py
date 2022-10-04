import csv
from enum import Enum
from typing import Dict, List


def is_num(v: any) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def float_try_parse(v: any, default_val: float) -> float:
    try:
        return float(v)
    except ValueError:
        return default_val


class SpecKeyEnum(Enum):
    TEST_NAME = 0
    TEST_NUM = 1
    TEST_NAME_NUM = 2


class SpecRow:
    def __init__(self, data: Dict[str, str]):
        self.test_text: str = data.get("TestText", "")
        self.test_num: int = data.get("TestNum", -1)
        self.low_limit: float = float_try_parse(data.get("LoLim"), float("-inf"))
        self.high_limit: float = float_try_parse(data.get("HiLim"), float("inf"))

    def get_key(self, key_type: SpecKeyEnum) -> str:
        if key_type == SpecKeyEnum.TEST_NAME:
            return self.test_text
        return ""


class Spec:
    _KEY_TYPE = SpecKeyEnum.TEST_NAME

    def __init__(self, spec_file_path: str):
        self.rows: List[SpecRow] = []
        self.lookup_dict: Dict[str, SpecRow] = {}
        with open(spec_file_path, "r") as f_in:
            reader = csv.DictReader(f_in)
            for d in reader:
                spec_row = SpecRow(d)
                self.rows.append(spec_row)
                self.lookup_dict[spec_row.get_key(self._KEY_TYPE)] = spec_row

    def compare(self, another_spec):
        for k, v in self.lookup_dict.items():
            if k in another_spec.lookup_dict.keys():
                another_spec_row = another_spec.lookup_dict[k]
                print(k, v.low_limit == another_spec_row.low_limit and v.high_limit == another_spec_row.high_limit,
                      v.low_limit, v.high_limit, another_spec_row.low_limit, another_spec_row.high_limit)


if __name__ == '__main__':
    s1 = Spec(r"C:\log\w236_rf_wlcsp_char_vs_qual_spec_compare\char.csv")
    s2 = Spec(r"C:\log\w236_rf_wlcsp_char_vs_qual_spec_compare\qual.csv")
    s2.compare(s1)
    print()
