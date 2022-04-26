import os
import csv
from Semi_ATE import STDF
from parser_base import ParserBase
from parser_csv import ParserCsv, ParserEcid


def test_parse_lot2():
    parser = ParserBase()
    stdf = os.path.abspath(os.path.join(__file__, os.pardir, "data", "lot2.stdf"))
    assert os.path.isfile(stdf)
    parser.parse(stdf)


def test_parse_lot3():
    parser = ParserBase()
    stdf = os.path.abspath(os.path.join(__file__, os.pardir, "data", "lot3.stdf"))
    assert os.path.isfile(stdf)
    parser.parse(stdf)


def test_with_ori_parser():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\TR7W6414.000_SYSB02BMJ000_20220116125443.stdf.gz")
    parser = ParserBase()
    assert os.path.isfile(stdf)
    parser.parse(stdf)


def test_parse_fd33():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\T6K160.00_STRV_T6K160-06G5_20220401102358_mod.stdf.gz")
    with open(r"C:\Users\nxf79056\Downloads\T6K160.00_STRV_T6K160-06G5_20220401102358_mod.adtf", "w") as f_out:
        for REC in STDF.records_from_file(stdf):
            f_out.write(str(REC))


def test_parse_f3():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\T6K160_BATCHCARD_T6K160-06G5_20220318113306.stdf.gz")
    parser = ParserCsv()
    parser.parse(stdf)

    with open(r"C:\workspace\io_leak\T6K160_LOOP200_20220308125623.csv", "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["Site", "TestNum", "TestTxt", "Result"])
        for k, v in parser.cache.items():
            for ptr in v:
                writer.writerow({
                    "Site": ptr["SITE_NUM"],
                    "TestNum": ptr["TEST_NUM"],
                    "TestTxt": str(ptr["TEST_TXT"]),
                    "Result": ptr["RESULT"]}
                )


def test_parse_ecid():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\T6K160_BATCHCARD_T6K160-06G5_20220318113306.stdf.gz")
    parser = ParserEcid()
    parser.parse(stdf)
    parser.export()
