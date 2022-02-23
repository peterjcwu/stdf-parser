import os
from parser_base import ParserBase
from parser_csv import ParserCsv


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


def test_parse_fd2():
    stdf = os.path.abspath(r"C:\workspace\stdf-parser\WLCSP1_IW612UK_A1_oldOS_20220221093327.stdf.gz")
    from Semi_ATE import STDF
    with open(r"c:\tmp\out2.atdf", "w") as f_out:
        for REC in STDF.records_from_file(stdf):
            f_out.write(str(REC))


def test_parse_f3():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\Cres_IW612UK_A1_oldOS_20220223164509.stdf.gz")
    parser = ParserCsv()
    parser.parse(stdf)
    import csv
    with open(r"C:\tmp\tmp.csv", "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["Site", "TestNum", "TestTxt", "Result"])
        for k, v in parser.cache.items():
            for ptr in v:
                writer.writerow({"Site": ptr["SITE_NUM"], "TestNum": ptr["TEST_NUM"], "TestTxt": ptr["TEST_TXT"], "Result": ptr["RESULT"]})

