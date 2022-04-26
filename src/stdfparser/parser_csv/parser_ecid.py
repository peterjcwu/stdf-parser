import csv
import re
import sys
from copy import copy
from collections import defaultdict
from parser_base import ParserBase


def ptr_handler(parser, record):
    # print('===========  Star of Record %s =======' % record.name)
    # for i, j in parser.data.items():
    #     print('< %s >  :   %s ---> %s' % (record.name, str(i), str(parser.data[i])))
    parser.cache[parser.data.get("TEST_NUM")].append(copy(parser.data))


def prr_handler(parser, record):
    x = parser.data["X_COORD"]
    y = parser.data["Y_COORD"]
    s = parser.data["SITE_NUM"]
    cache_one_site = parser.cache.pop(str(s), None)

    if cache_one_site is None:
        cache_one_site = {'ECID_VALID': '', 'ECID_FAB': '', 'ECID_LOT_ID': '', 'ECID_WAFER_ID': '', 'ECID_X_COORD': '', 'ECID_Y_COORD': ''}

    cache_one_site["die_x"] = x
    cache_one_site["die_y"] = y
    cache_one_site["site"] = s
    parser.rows.append(cache_one_site.copy())
    parser.counter += 1
    # if parser.counter >= 100:
    #     parser.export()
    #     sys.exit()


def dtr_handler(parser, record):
    # print('===========  Star of Record %s =======' % record.name)
    text = parser.data["TEXT_DAT"].decode()
    if not text.startswith("ECID"):
        return

    m = re.search(r"^ECID_VALID,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_VALID"] = m.group("val")

    m = re.search(r"^ECID_FAB,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_FAB"] = m.group("val")

    m = re.search(r"^ECID_LOT_ID,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_LOT_ID"] = m.group("val")

    m = re.search(r"^ECID_WAFER_ID,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_WAFER_ID"] = m.group("val")

    m = re.search(r"^ECID_X_COORD,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_X_COORD"] = m.group("val")

    m = re.search(r"^ECID_Y_COORD,0,(?P<site>\d+),(?P<val>.*)", text, re.I)
    if m:
        parser.cache[m.group("site")]["ECID_Y_COORD"] = m.group("val")


class ParserEcid(ParserBase):
    def __init__(self):
        ParserBase.__init__(self)
        self.handlers = {
            # "Ptr": ptr_handler,
            "Dtr": dtr_handler,
            "Prr": prr_handler,
        }
        self.cache = defaultdict(dict)
        self.rows = []
        self.counter = 0

    def take(self, typ_sub):
        record = self.Rec_Dict.get(typ_sub)
        if record is None or record.name not in self.handlers:
            return
        handler = self.handlers.get(record.name)
        handler(self, record)

    def export(self):
        with open(r"C:\tmp\o.csv", "w", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=["die_x", "die_y", "site", 'ECID_VALID', 'ECID_FAB', 'ECID_LOT_ID', 'ECID_WAFER_ID', 'ECID_X_COORD', 'ECID_Y_COORD'])
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)


if __name__ == '__main__':
    p = ParserEcid()
    p.parse(r"C:\workspace\_backup\w214_ecid_masking_T6K160\T6K160_First_T6K160-06G5_20220331130126.stdf.gz")
    p.export()
